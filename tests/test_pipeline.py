from lakehouse_pipeline.pipeline import connect, ingest, metrics

def test_latest_version_and_replay():
    db = connect()
    rows = [
      {"event_id":"1","order_id":"a","customer_id":"c","amount":"8","status":"placed","version":"1"},
      {"event_id":"2","order_id":"a","customer_id":"c","amount":"8","status":"paid","version":"2"},
    ]
    assert ingest(db, rows)["accepted"] == 2
    assert ingest(db, rows)["duplicates"] == 2
    assert metrics(db) == [("c",1,8.0)]

def test_invalid_input_rejected():
    db = connect()
    assert ingest(db,[{"event_id":"1"}])["rejected"] == 1
