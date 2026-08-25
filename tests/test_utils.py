import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import parse_choices


def test_parse_choices():
    assert parse_choices("1,2", {"1", "2", "3"}, "3") == {"1", "2"}
    assert parse_choices(" 1 , 2 ", {"1", "2", "3"}, "3") == {"1", "2"}
    assert parse_choices("3", {"1", "2", "3"}, "3") == {"FULL"}
    assert parse_choices("1,3", {"1", "2", "3"}, "3") == {"FULL"}

    try:
        parse_choices("9", {"1", "2", "3"}, "3")
        assert False, "expected ValueError for out-of-range choice"
    except ValueError:
        pass

    try:
        parse_choices("x", {"1", "2", "3"}, "3")
        assert False, "expected ValueError for non-digit choice"
    except ValueError:
        pass


if __name__ == "__main__":
    test_parse_choices()
    print("ok")
