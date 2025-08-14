class PaymentSystem:
    def charge(self, amount: float, meta=None):
        """
        Списывает указанную сумму.
        :param amount: сумма для списания
        :param meta: произвольные метаданные
        """
        return {
            "status": "charged",
            "amount": amount,
            "meta": meta
        }

    def process(self, payload):
        """
        Обрабатывает платёж или транзакцию.
        :param payload: данные транзакции
        """
        return {
            "status": "processed",
            "payload": payload
        }

    def refund(self, amount: float, reason: str = ""):
        """
        Возвращает указанную сумму.
        :param amount: сумма для возврата
        :param reason: причина возврата
        """
        return {
            "status": "refunded",
            "amount": amount,
            "reason": reason
        }
