class Region():
    supported_regions = ('na', 'lan')

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
        return ''
