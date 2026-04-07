def recommend_articles(article, user):
    history_ids = user.viewhistory_set.values_list('article_id', flat=True)
    return article.__class__.objects.exclude(id__in=history_ids)[:5]