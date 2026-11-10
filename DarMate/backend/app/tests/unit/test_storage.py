import pytest

from app.application.interfaces.services import UploadedFile
from app.core.exceptions import NotFoundError, ValidationFailedError
from app.infrastructure.external_services.services import LocalFileStorage

MIMES = {"image/png": ".png", "image/jpeg": ".jpg"}
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 50


def test_valid_png_saved_privately(tmp_path):
    st = LocalFileStorage(str(tmp_path))
    path = st.save("x", UploadedFile("a.png", "image/png", PNG), MIMES, 1000, private=True)
    assert path.startswith("private/x/") and path.endswith(".png")
    assert st.read(path) == PNG


@pytest.mark.parametrize("file", [
    UploadedFile("a.exe", "application/x-msdownload", b"MZ"),
    UploadedFile("a.png", "image/png", b"not really a png"),          # mauvaise signature
    UploadedFile("a.jpg", "image/png", PNG),                          # extension != type
    UploadedFile("a.png", "image/png", b""),                          # vide
    UploadedFile("a.png", "image/png", PNG + b"0" * 2000),            # trop gros
])
def test_rejected_files(tmp_path, file):
    with pytest.raises(ValidationFailedError):
        LocalFileStorage(str(tmp_path)).save("x", file, MIMES, 1000, private=False)


def test_path_traversal_blocked(tmp_path):
    (tmp_path.parent / "secret.txt").write_text("s")
    with pytest.raises(NotFoundError):
        LocalFileStorage(str(tmp_path)).read("../secret.txt")
