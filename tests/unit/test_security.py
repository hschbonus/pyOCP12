from epicevents import security


# Test si un mot de passe haché puis vérifie renvoie True
def test_hash_and_verify_password():
    plain_password = "mon_mot_de_passe"
    hashed_password = security.hash_password(plain_password)
    assert security.verify_password(hashed_password, plain_password) is True
    assert security.verify_password(hashed_password, "mot_de_passe_incorrect") is False
