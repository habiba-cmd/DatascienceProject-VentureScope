from src.concept import match_categories
from src.annotation import prepare_annotation_sheet
import pandas as pd

def test_category_matching():
    result=match_categories('durable luggage',['Luggage','Dog Food','Beauty'])
    assert result.iloc[0]['category']=='Luggage'

def test_annotation_template_is_unlabelled():
    df=pd.DataFrame({'text':['a useful example of a long review about a product','another example of a customer experience that is real'],'sentiment_label':[1,2]})
    sheet=prepare_annotation_sheet(df,n=2)
    assert (sheet.label_primary=='').all()
