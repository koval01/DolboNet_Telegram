from random import choice

def random_emoj_tg():
    emoj_list = [
        '🗿',
        '👌',
        '🙈',
        '👽',
        '🗿',
        '😎',
        '💩',
        '🐒',
        '🦥',
        '🪓',
        '❤️', # Червоне
        '🧡', # Помаранчеве
        '💛', # Жовте
        '💚', # Зелене
        '💙', # Синє
        '💜', # Фіолетове
        '🖤', # Чорне
        '🤍', # Біле
        '🍑',
        '🍆',
        '🍌',
        '⚰️',
        '😍'
    ]
    emoj_send1 = choice(emoj_list)
    return emoj_send1