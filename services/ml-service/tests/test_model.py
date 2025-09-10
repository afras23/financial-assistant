from app.model import predict_category

def test_predict_smoke():
    assert isinstance(predict_category("Latte at Starbucks"), str)
