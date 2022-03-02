from elasticsearch_dsl import analyzer, token_filter, char_filter


letters_mapping = char_filter("letters", type="mapping", mappings=["ё => е", "Ё => Е"])

stopwords = token_filter(
    "stopwords", type="stop", stopwords=["_russian_", "_english_"], ignore_case=True
)

russian_stemmer = token_filter("russian_stemmer", type="stemmer", language="russian")

english_stemmer = token_filter("english_stemmer", type="stemmer", language="english")

fts_analyzer = analyzer(
    "fts",
    type="custom",
    tokenizer="standard",
    char_filter=[letters_mapping],
    filter=["lowercase", stopwords, russian_stemmer, english_stemmer],
)
