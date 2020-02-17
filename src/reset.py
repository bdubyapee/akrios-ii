#! usr/bin/env python
# Project: Akrios
# Filename: reset.py
# 
# File Description: Module dealing with resets for mobiles, objects, shops, etc.
# 
# By: Jubelo

from collections import namedtuple
import logging
import json
import uuid

import olc

log = logging.getLogger(__name__)

# Define some named tuples for various reset values.

ResetType = namedtuple("ResetType", "name")

reset_type = {"mobile": ResetType("mobile"),
              "object": ResetType("object"),
              "shop": ResetType("shop")}


class BaseReset(object):
    def __init__(self):
        super().__init__()
        self.aid = str(uuid.uuid4())
        self.reset_vnum = 0
        self.target_vnum = 0
        self.target_max_amount = 0
        self.target_type = None
        self.target_loc_vnum = 0

    def base_to_json(self):
        jsonable = {"reset_vnum": self.reset_vnum,
                    "target_vnum": self.target_vnum,
                    "target_max_amount": self.target_max_amount,
                    "target_type": self.target_type,
                    "target_loc_vnum": self.target_loc_vnum}
        return jsonable


class MobileReset(BaseReset):
    def __init__(self, area=None, data=None):
        super().__init__()
        self.area = area

        if data is not None:
            self.load(data)

    def to_json(self):
        jsonable = self.base_to_json()

        return json.dumps(jsonable, sort_keys=True, indent=4)

    def load(self, data):
        for eachkey, eachvalue in json.loads(data).items():
            setattr(self, eachkey, eachvalue)

        # needed?
        if type(self.target_loc_vnum) is str:
            self.target_loc_vnum = int(self.target_loc_vnum)

    async def execute(self):
        if self.target_vnum not in self.area.mobilelist_by_vnum_index:
            log.error(f"Unable to find mobile vnum {self.target_vnum}")
            return

        if self.target_loc_vnum not in self.area.roomlist:
            log.error(f"Mobile Unable to find room vnum {self.target_loc_vnum}")
            log.error(f"target_loc_vnum type = {type(self.target_loc_vnum)}")
            log.error(f"roomlist = {self.area.roomlist}")
            return

        # ADD: Count current mobiles of this vnum, if at or exceeding max then bail out.

        loc = self.target_loc_vnum
        await self.area.mobilelist_by_vnum_index[self.target_vnum].create_instance(location=loc)


class ObjectReset(BaseReset):
    def __init__(self, area=None, data=None):
        super().__init__()
        self.area = area
        self.target_loc_is = ''
        self.target_mobile_wear = False

        if data is not None:
            self.load(data)

    def to_json(self):
        jsonable = self.base_to_json()
        jsonable["target_loc_is"] = self.target_loc_is
        jsonable["target_mobile_wear"] = self.target_mobile_wear

        return json.dumps(jsonable, sort_keys=True, indent=4)

    def load(self, data):
        for eachkey, eachvalue in json.loads(data).items():
            setattr(self, eachkey, eachvalue)

        # needed?
        if type(self.target_loc_vnum) is str:
            self.target_loc_vnum = int(self.target_loc_vnum)

        if self.target_mobile_wear == "true":
            self.target_mobile_wear = True
        else:
            self.target_mobile_wear = False

    async def execute(self):
        if self.target_vnum not in self.area.objectlist_by_vnum_index:
            log.error(f"Unable to find object vnum {self.target_vnum}")
            return

        if self.target_loc_is == 'room' and self.target_loc_vnum not in self.area.roomlist:
            log.error(f"Object Unable to find room vnum {self.target_loc_vnum}")
            log.error(f"target_loc_vnum type = {type(self.target_loc_vnum)}")
            log.error(f"roomlist = {self.area.roomlist}")
            return

        mli = self.area.mobilelist_by_vnum_index

        if self.target_loc_is == 'mobile' and self.target_loc_vnum not in mli:
            log.error(f"Unable to find mobile vnum {self.target_loc_vnum}")
            return

        # ADD: Count current objects of this vnum, if at or exceeding max then bail out.

        await self.area.objectlist_by_vnum_index[self.target_vnum].create_instance(self)


class Reset(olc.Editable):
    CLASS_NAME = "__Reset__"
    FILE_VERSION = 1

    def __init__(self, area=None):
        super().__init__()
        self.json_version = Reset.FILE_VERSION
        self.json_class_name = Reset.CLASS_NAME
        self.area = area
        self.aid = str(uuid.uuid4())
        self.mobile_list = {}
        self.object_list = {}
        self.shop_list = {}
        self.commands = {"target_type": ("string", reset_type),
                         "mobile": ("string", None),
                         "object": ("string", None),
                         "shop": ("string", None)}

    def to_json(self):
        if self.json_version == 1:

            mob_list = {int(k): v.to_json() for k, v in self.mobile_list.items()}
            obj_list = {int(k): v.to_json() for k, v in self.object_list.items()}
            shp_list = {int(k): v.to_json() for k, v in self.shop_list.items()}

            jsonable = {"json_version": self.json_version,
                        "json_class_name": self.json_class_name,
                        "aid": self.aid,
                        "mobile_list": mob_list or {},
                        "object_list": obj_list or {},
                        "shop_list": shp_list or {}}

            return json.dumps(jsonable, sort_keys=True, indent=4)

    async def load(self, data):
        for eachkey, eachvalue in json.loads(data).items():
            setattr(self, eachkey, eachvalue)

        log.debug(f"Loading reset {self.aid} in {self.area.name}")

        self.mobile_list = {int(k): MobileReset(self.area, v) for k, v in self.mobile_list.items()}
        self.object_list = {int(k): ObjectReset(self.area, v) for k, v in self.object_list.items()}
        # self.shop_list = {int(k): ShopReset(self.area, v) for k, v in self.shop_list.items()}

        if self.mobile_list:
            for each_reset in self.mobile_list.values():
                await each_reset.execute()
        if self.object_list:
            for each_reset in self.object_list.values():
                await each_reset.execute()

        self.area.resetlist = self

    def display(self):
        return(f"{{BArea{{x: {self.area.name}\n"
               f"{{BAid{{x: {self.aid}\n")
