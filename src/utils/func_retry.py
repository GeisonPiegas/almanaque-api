import time


def retry(func, *args, max_retries=3, delay=2, **kwargs):
    attempts = 0
    while attempts < max_retries:
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            attempts += 1
            print(f"Tentativa {attempts} falhou: {e}")
            if attempts >= max_retries:
                raise Exception("Máximo de tentativas excedido") from e
            time.sleep(delay)
