from pathlib import Path
from cryptography.fernet import Fernet


class EncryptionManager:

    def __init__(self, path_to_key: str) -> None:
        self._key_path = Path(path_to_key)

    def _ensure_key_exists(self) -> None:
        self._key_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._key_path.exists():
            key = Fernet.generate_key()

            with open(self._key_path, "wb") as file:
                file.write(key)

    def _load_key(self) -> bytes:
        self._ensure_key_exists()

        with open(self._key_path, "rb") as file:
            return file.read()

    def encrypt_text(self, decrypted_text: str) -> str:
        key: bytes = self._load_key()

        fernet = Fernet(key)
        return fernet.encrypt(decrypted_text.encode("utf-8")).decode("utf-8")

    def decrypt_text(self, encrypted_text: str) -> str:
        key = self._load_key()

        fernet = Fernet(key)
        return fernet.decrypt(encrypted_text.encode("utf-8")).decode("utf-8")
