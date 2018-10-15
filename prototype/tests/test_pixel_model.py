from geometry_constructor import Models


def test_initialise_model():
    model = Models.PixelModel()
    assert model.rowCount() == 1


def test_add_pixel():
    model = Models.PixelModel()
    model.add_pixel("Fib", "0,1,1 ,2, 3, 5 ")
    assert model.rowCount() == 2
    assert model.my_list[1] == Models.Pixel(name="Fib", faces=[0, 1, 1, 2, 3, 5])
    assert Models.Pixel(name="Fib", faces=[0, 1, 1, 2, 3, 5]) in model.my_list


def test_remove_pixel():
    model = Models.PixelModel()
    model.add_pixel("Fib", "0,1,1 ,2, 3, 5 ")
    model.remove_pixel(1)
    assert model.rowCount() == 1
    assert Models.Pixel(name="Fib", faces=[0, 1, 1, 2, 3, 5]) not in model.my_list
