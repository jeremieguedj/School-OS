from __future__ import annotations

import unittest
from email.message import EmailMessage

from school_os.delivery import DeliveryError, ExactDeliveryRequest, deliver_exact


def raw_message(request: ExactDeliveryRequest) -> bytes:
    message = EmailMessage()
    message["To"] = ", ".join(request.to)
    if request.cc:
        message["Cc"] = ", ".join(request.cc)
    if request.bcc:
        message["Bcc"] = ", ".join(request.bcc)
    message["Subject"] = request.subject
    message.set_content(request.text.decode("utf-8"), cte="8bit")
    message.add_alternative(request.html.decode("utf-8"), subtype="html", cte="8bit")
    return message.as_bytes()


class DeliveryRuntimeTests(unittest.TestCase):
    def request(self, key: str = "daily-1", variant: str = "manual") -> ExactDeliveryRequest:
        return ExactDeliveryRequest.build(
            key=key, variant=variant, to=("parent@example.invalid",),
            subject=f"Test brief [School-OS:{key}]", text=b"Plain body\n", html=b"<p>HTML body</p>\n",
        )

    def harness(self, sent: dict[str, dict] | None = None):
        ledgers: list[dict] = []
        effects: list[dict] = []
        messages = sent or {}
        def persist_ledger(value): ledgers.append(dict(value))
        def read_ledger(): return dict(ledgers[-1]) if ledgers else None
        def persist_effect(value): effects.append(dict(value))
        def read_effect(): return dict(effects[-1]) if effects else None
        def read_sent(identity): return messages[identity]
        return ledgers, effects, messages, persist_ledger, read_ledger, persist_effect, read_effect, read_sent

    def test_persists_pending_intent_and_effect_before_send_then_suppresses_replay(self) -> None:
        request = self.request()
        ledgers, effects, messages, persist, read, persist_effect, read_effect, read_sent = self.harness()
        def send(value):
            self.assertEqual("pending", read()["status"])
            self.assertEqual("pending", read_effect()["outcome"])
            messages["m1"] = {"id": "m1", "label_ids": ["SENT"], "raw": raw_message(value)}
            return {"id": "m1"}
        result = deliver_exact(request, read_ledger=read, persist_ledger=persist, persist_effect_checkpoint=persist_effect, read_effect_checkpoint=read_effect, send=send, read_sent=read_sent, search_sent=lambda _token: ((), None))
        self.assertEqual("confirmed", result["outcome"])
        self.assertEqual({"effect": "mail.send", "fingerprint": request.fingerprint, "key": request.key, "outcome": "confirmed", "provider_message_id": "m1"}, read_effect())
        replay = deliver_exact(request, read_ledger=read, persist_ledger=persist, persist_effect_checkpoint=persist_effect, read_effect_checkpoint=read_effect, send=lambda _: self.fail("duplicate send"), read_sent=read_sent, search_sent=lambda _token: ((), None))
        self.assertEqual("suppressed", replay["outcome"])

    def test_unknown_send_never_retries_and_recovery_requires_one_full_context_match(self) -> None:
        request = self.request()
        ledgers, effects, messages, persist, read, persist_effect, read_effect, read_sent = self.harness()
        with self.assertRaisesRegex(DeliveryError, "unknown"):
            deliver_exact(request, read_ledger=read, persist_ledger=persist, persist_effect_checkpoint=persist_effect, read_effect_checkpoint=read_effect, send=lambda _: (_ for _ in ()).throw(OSError("lost")), read_sent=read_sent, search_sent=lambda _token: ((), None))
        self.assertEqual("pending", read()["status"])
        messages["m1"] = {"id": "m1", "label_ids": ["SENT"], "raw": raw_message(request)}
        result = deliver_exact(request, read_ledger=read, persist_ledger=persist, persist_effect_checkpoint=persist_effect, read_effect_checkpoint=read_effect, send=lambda _: self.fail("blind retry"), read_sent=read_sent, search_sent=lambda token: (({"id": "m1"},), None))
        self.assertEqual("reconciled", result["outcome"])
        self.assertEqual("confirmed", read_effect()["outcome"])

        pending = dict(ledgers[0]); ledgers[:] = [pending]; effects[:] = [effects[0]]
        with self.assertRaisesRegex(DeliveryError, "0 exact matches"):
            deliver_exact(request, read_ledger=read, persist_ledger=persist, persist_effect_checkpoint=persist_effect, read_effect_checkpoint=read_effect, send=lambda _: self.fail("blind retry"), read_sent=read_sent, search_sent=lambda token: ((), None))

    def test_equal_bodies_with_different_keys_are_distinct(self) -> None:
        first = self.request("key-a", "manual")
        second = self.request("key-b", "scheduled")
        self.assertNotEqual(first.fingerprint, second.fingerprint)
        self.assertEqual("multipart/alternative", first.gmail_args()["payload"]["mime_type"])

    def test_abrupt_stop_after_provider_acceptance_leaves_may_have_applied_gate(self) -> None:
        request = self.request()
        ledgers, effects, messages, persist, read, persist_effect, read_effect, read_sent = self.harness()
        def accepted_then_process_stops(value):
            messages["m1"] = {"id": "m1", "label_ids": ["SENT"], "raw": raw_message(value)}
            raise SystemExit(99)
        with self.assertRaises(SystemExit):
            deliver_exact(request, read_ledger=read, persist_ledger=persist, persist_effect_checkpoint=persist_effect, read_effect_checkpoint=read_effect, send=accepted_then_process_stops, read_sent=read_sent, search_sent=lambda _token: ((), None))
        self.assertEqual("pending", read()["status"])
        with self.assertRaisesRegex(DeliveryError, "0 exact matches"):
            deliver_exact(request, read_ledger=read, persist_ledger=persist, persist_effect_checkpoint=persist_effect, read_effect_checkpoint=read_effect, send=lambda _: self.fail("fresh process retried send"), read_sent=read_sent, search_sent=lambda _token: ((), None))

    def test_crash_before_effect_checkpoint_can_dispatch_but_pending_effect_cannot(self) -> None:
        request = self.request()
        ledgers, effects, messages, persist, read, persist_effect, read_effect, read_sent = self.harness()
        ledgers.append({
            "fingerprint": request.fingerprint, "intent": request.intent(),
            "provider_message_id": None, "schema_version": 1, "status": "pending",
        })
        calls = 0
        def send(value):
            nonlocal calls
            calls += 1
            self.assertEqual("pending", read_effect()["outcome"])
            messages["m1"] = {"id": "m1", "label_ids": ["SENT"], "raw": raw_message(value)}
            return {"id": "m1"}
        self.assertEqual("confirmed", deliver_exact(
            request, read_ledger=read, persist_ledger=persist,
            persist_effect_checkpoint=persist_effect, read_effect_checkpoint=read_effect,
            send=send, read_sent=read_sent, search_sent=lambda _token: ((), None),
        )["outcome"])
        self.assertEqual(1, calls)

    def test_provider_identity_mismatch_never_confirms_or_heals_delivery_state(self) -> None:
        request = self.request()
        ledgers, effects, _messages, persist, read, persist_effect, read_effect, _read_sent = self.harness()
        mismatched = lambda _identity: {
            "id": "different-id", "label_ids": ["SENT"], "raw": raw_message(request),
        }
        call = dict(
            request=request, read_ledger=read, persist_ledger=persist,
            persist_effect_checkpoint=persist_effect, read_effect_checkpoint=read_effect,
            send=lambda _: {"id": "returned-id"}, read_sent=mismatched,
            search_sent=lambda _token: ((), None),
        )
        with self.assertRaisesRegex(DeliveryError, "provider identity disagrees"):
            deliver_exact(**call)
        pending_ledger = dict(read())
        pending_effect = dict(read_effect())
        self.assertEqual("pending", pending_ledger["status"])
        self.assertEqual("pending", pending_effect["outcome"])

        ledgers[:] = [{**pending_ledger, "status": "confirmed", "provider_message_id": "returned-id"}]
        effects[:] = [pending_effect]
        with self.assertRaisesRegex(DeliveryError, "provider identity disagrees"):
            deliver_exact(**{**call, "send": lambda _: self.fail("duplicate send")})
        self.assertEqual("pending", read_effect()["outcome"])

        ledgers[:] = [pending_ledger]
        effects[:] = [pending_effect]
        with self.assertRaisesRegex(DeliveryError, "0 exact matches"):
            deliver_exact(**{
                **call, "send": lambda _: self.fail("blind retry"),
                "search_sent": lambda _token: (({"id": "returned-id"},), None),
            })
        self.assertEqual("pending", read()["status"])
        self.assertEqual("pending", read_effect()["outcome"])


if __name__ == "__main__":
    unittest.main()
