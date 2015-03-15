class Region():
    supported_regions = (
        'na',
        'lan',
        'las',
        'euw',
        'eune',
        'kr',
        'oce',
        'ru',
        'tr'
    )

    @staticmethod
    def is_region_valid(region):
        return region.lower() in Region.supported_regions

    @staticmethod
    def to_platform_id(region):
        """
            For some api calls, the parameter requested is a platform id
            which is basically the region name + an ID number in upper case.
        """
        region = region.lower()
        if region == 'na':
            return 'NA1'
        elif region == 'lan':
            return 'LA1'
        elif region == 'br':
            return 'BR1'
        elif region == 'las':
            return 'LA2'
        elif region == 'oce':
            return 'OC1'
        elif region == 'eune':
            return 'EUN1'
        elif region == 'tr':
            return 'TR1'
        elif region == 'ru':
            return 'RU'
        elif region == 'euw':
            return 'EUW1'
        elif region == 'kr':
            return 'KR'
        return ''
