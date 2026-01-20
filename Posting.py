import shelve
from datetime import datetime, timedelta
from typing import final


class PostingForm:
    count_id = 0

    # creating function to set the count_id w existing id
    @classmethod
    def load_count_id(cls):
        db = shelve.open('bookings', 'c')
        posted_jobs = db.get('Jobs', {})

        if posted_jobs:
            cls.count_id = max(posted_jobs.keys())

        db.close()

    def __init__(self, co_name, position, quantity, description, pay_rate, date, start_time, end_time):
        PostingForm.count_id += 1
        self.__posting_id = PostingForm.count_id
        self.__co_name = co_name
        self.__position = position
        self.__quantity = quantity
        self.__description = description
        self.__pay_rate = pay_rate
        self.__date = date
        self.__start_time = start_time
        self.__end_time = end_time
        # self.__booked = False
        self.__booked_by = []

    # accessor methods
    def get_posting_id(self):
        return self.__posting_id

    def get_co_name(self):
        return self.__co_name

    def get_position(self):
        return self.__position

    def get_quantity(self):
        return self.__quantity

    def get_description(self):
        return self.__description

    def get_pay_rate(self):
        return self.__pay_rate

    def get_date(self):
        return self.__date

    def get_start_time(self):
        return self.__start_time

    def get_end_time(self):
        return self.__end_time

    def get_booked_by(self):
        return self.__booked_by

    # def is_booked(self):
    #     return self.__booked

    # cancel booking function
    def cancel_booking(self, user_id):
        if user_id in self.__booked_by:
            self.__booked_by.remove(user_id)
            self.__quantity += 1


    # function to calculate total hours
    def calc_total_hrs(self):
        stime_delta = timedelta(hours=self.__start_time.hour, minutes=self.__start_time.minute)
        etime_delta = timedelta(hours=self.__end_time.hour, minutes=self.__end_time.minute)

        time_diff = etime_delta - stime_delta
        total_hrs = time_diff.total_seconds() / 3600
        return total_hrs

    # mutator methods
    def set_posting_id(self, posting_id):
        self.__posting_id = posting_id

    def set_co_name(self, company_name):
        self.__co_name = company_name

    def set_position(self, position):
        self.__position = position

    def set_quantity(self, quantity):
        self.__quantity = quantity

    def set_description(self, description):
        self.__description = description

    def set_pay_rate(self, pay_rate):
        self.__pay_rate = pay_rate

    def set_date(self, start_date):
        self.__date = start_date

    def set_start_time(self, start_time):
        self.__start_time = start_time

    def set_end_time(self, end_time):
        self.__end_time = end_time

    # def set_booked(self, booked):
    #     self.__booked = booked

    def set_booked_by(self, user_name):
        if user_name not in self.__booked_by:
            self.__booked_by.append(user_name)