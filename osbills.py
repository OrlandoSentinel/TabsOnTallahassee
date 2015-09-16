    def accept_response(self, response):
        normal = super(FLBillScraper, self).accept_response(response)
        bill_check = True
        text_check = True

        if not response.url.lower().endswith('pdf'):
            if response.url.startswith("http://flsenate.gov/Session/Bill/20"):
                bill_check = "tabBodyVoteHistory" in response.text

            text_check = ('page you have requested has encountered an error.'
                not in response.text)

        if not (normal and bill_check and text_check)
            raise Exception('Response was invalid')
        return valid
