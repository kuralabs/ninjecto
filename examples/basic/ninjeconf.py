from ninjecto.plugins.filters import register


@register('tomelize')
def tomelize(value):
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    if isinstance(value, str):
        return '"{}"'.format(value.replace('"', '\\"'))
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value

    if value is None:
        raise ValueError(
            'TOML doens\'t support NULL values. '
            'Leave key out of assignement.'
        )

    raise RuntimeError(
        'Unknown value type "{}" for "{}" to tomelize'.format(
            type(value), value
        )
    )
