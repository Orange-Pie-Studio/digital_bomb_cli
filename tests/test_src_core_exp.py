from digital_bomb.core.exp import calculate_exp

def test_calculate_exp():
    difficult = "easy"
    turn = 15
    scope = "[0~100]"
    situation = "victory"
    exp = calculate_exp(difficult, turn, scope, situation)
    assert exp == 1200