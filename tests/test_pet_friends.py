from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password, invalid_auth_key
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем, что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert "key" in result


def test_get_api_key_for_invalid_user(email=invalid_email, password=invalid_password):
    """ Проверяем, что запрос api ключа, с использованием невалидных email и пароля,
    возвращает статус 403 и в результате не содержится слово key"""

    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert "key" not in result


def test_get_all_pets_with_valid_key(filter=""):
    """ Проверяем, что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее, используя этот ключ,
    запрашиваем список всех питомцев и проверяем, что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result["pets"]) > 0


def test_get_all_pets_with_invalid_key(filter=""):
    """ Проверяем, что запрос всех питомцев с использованием невалидного api ключа,
    возвращает статус 403 и в результате не содержится слово pets """

    status, result = pf.get_list_of_pets(invalid_auth_key, filter)
    assert status == 403
    assert "pets" not in result


def test_add_new_pet_with_valid_data(name="Шпротик", animal_type="кот",
                                     age="5", pet_photo="images/cat2.jpg"):
    """Проверяем, что можно добавить питомца с корректными данными"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result["name"] == name


def test_add_new_pet_with_invalid_age(name="Шпротик", animal_type="кот",
                                      age="-5", pet_photo="images/cat2.jpg"):
    """Проверяем добавление питомца с некорректными данными (возраст - отрицательное число)"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert int(age) < 0


def test_add_new_pet_with_invalid_photo(name="Шпротик", animal_type="кот",
                                         age="5", pet_photo="images/error3.txt"):
    """Проверяем добавление питомца с некорректными данными (фото питомца - текстовый файл)"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert pet_photo not in result


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Соня", "кошка", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 200
    assert pet_id not in my_pets.values()


def test_delete_self_pet_with_invalid_key():
    """Проверяем возможность удаления питомца с использованием невалидного api ключа"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Соня", "кошка", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Удаление питомца с использованием невалидного ключа
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(invalid_auth_key, pet_id)

    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 403
    assert pet_id not in my_pets.values()


def test_delete_self_pet_with_invalid_id():
    """Проверяем возможность удаления питомца с использованием невалидного id"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Соня", "кошка", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Удаление питомца с использованием невалидного id
    pet_id = "invalid_id"
    status, _ = pf.delete_pet(auth_key, pet_id)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name="Степа", animal_type="кот", age="5"):
    """Проверяем возможность обновления информации о питомце"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets["pets"]) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets["pets"][0]["id"], name, animal_type, age)

        assert status == 200
        assert result["name"] == name
    else:
        raise Exception("Ваш список питомцев пустой")


def test_update_self_pet_info_with_invalid_id(name="Степа", animal_type="кот", age="5"):
    """Проверяем возможность обновления информации о питомце с использованием невалидного id"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets["pets"]) > 0:
        pet_id = "invalid_id"
        status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)
        assert status == 400
        assert pet_id not in result
    else:
        raise Exception("Ваш список питомцев пустой")


def test_add_new_pet_simple_with_valid_data(name="Анфиса", anymal_type="кошка", age="3"):
    """Проверяем, что можно добавить питомца с корректными данными (без фото)"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_simple(auth_key, name, anymal_type, age)
    assert status == 200
    assert result['name'] == name


def test_add_new_pet_simple_with_invalid_key(name="Анфиса", anymal_type="кошка", age="3"):
    """Проверяем добавление питомца (без фото) с использованием невалидного api ключа """

    status, result = pf.add_new_pet_simple(invalid_auth_key, name, anymal_type, age)
    assert status == 403
    assert "name" not in result


def test_add_photo_of_pet_with_valid_data(pet_photo="images/cat3.jpg"):
    """Проверяем, что можно добавить фото питомца с корректными данными"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets["pets"]) > 0:
        pet_id = my_pets['pets'][0]['id']
        status, result = pf.add_photo_of_pet(auth_key, pet_id, pet_photo)
        assert status == 200
        assert pet_photo is not None
    else:
        raise Exception("Ваш список питомцев пустой")


def test_add_photo_of_pet_with_invalid_data(pet_photo="images/error3.txt"):
    """Проверяем добавление фото питомца с некорректными данными (фото питомца - текстовый файл)"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets["pets"]) > 0:
        pet_id = my_pets['pets'][0]['id']
        status, result = pf.add_photo_of_pet(auth_key, pet_id, pet_photo)
        assert status == 500
        assert pet_photo not in my_pets
    else:
        raise Exception("Ваш список питомцев пустой")


def test_add_photo_of_pet_with_invalid_id(pet_photo="images/cat3.jpg"):
    """Проверяем добавление фото питомца с некорректным id"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets["pets"]) > 0:
        pet_id = "invalid_id"
        status, result = pf.add_photo_of_pet(auth_key, pet_id, pet_photo)
        assert status == 500
        assert pet_photo not in my_pets
    else:
        raise Exception("Ваш список питомцев пустой")




