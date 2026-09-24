from app.celery_app import celery_app


@celery_app.task
def add_numbers(a, b):
    return a + b


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True
)
def send_payment_notification(self, payment_id: int, status: str):

    print(
        f"Payment notification sent | "
        f"Payment ID: {payment_id} | "
        f"Status: {status}"
    )

    return {
        "payment_id": payment_id,
        "status": status,
        "message": "Payment notification sent"
    }