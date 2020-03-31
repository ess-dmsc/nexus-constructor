from nexus_constructor.model.component import Component


def test_component_set_item_with_brackets_works_with_another_component():
    comp1 = Component("comp1")

    comp2 = Component("comp2")

    comp1[comp2.name] = comp2

    assert comp1[comp2.name] == comp2


def test_component_set_item_with_brackets_works_with_string():
    comp1 = Component("comp1")
    some_field_value = "test"
    # TODO: this should fail when setting before getting
    comp1["some_field"] = some_field_value
    assert comp1["some_field"] == some_field_value
