"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

from collections import defaultdict
from yosai.core import (
    serialize_abcs,
    subject_abcs,
)
from marshmallow import Schema, fields, post_dump, pre_load, post_load
import copy


class SimpleIdentifierCollection(subject_abcs.MutableIdentifierCollection,
                                 serialize_abcs.Serializable):

    # yosai.core.re-ordered the argument list:
    def __init__(self, realm_name=None, identifier=None,
                 identifier_collection=None):
        """
        :type realm_name: a String
        :type identifier: a Set or scalar
        :type identifier_collection: a SimpleIdentifierCollection
        """
        self.realm_identifier = defaultdict(set)
        self._primary_identifier = None
        self.add(realm_name, identifier, identifier_collection)

    # yosai.core.omits get_identifier_lazy because it uses a defaultdict(set)
    # yosai.core.omits asSet, asList, and toString  -- TBD

    @property
    def primary_identifier(self):
        if (not self._primary_identifier):
            try:
                # DG:  shiro arbitrarily selects for missing primary identifier
                identifier = self.realm_identifier.values()
                primary_identifier = next(iter(next(iter(identifier))))
            except (AttributeError, TypeError):
                msg = "failed to arbitrarily obtain primary identifier"
                print(msg)
                # log warning here
                return None
            else:
                self._primary_identifier = primary_identifier
                return primary_identifier
        return self._primary_identifier

    # there is no primary_identifier setter because it should not be manually
    # set

    # yosai.core.combines add and addAll functionality:
    def add(self, realm_name=None, identifier=None,
            identifier_collection=None):
        """
        :type realm_name: a String
        :type identifier: a Set or scalar
        :type identifier_collection: a SimpleIdentifierCollection
        """
        if isinstance(identifier_collection,
                      subject_abcs.MutableIdentifierCollection):
            new_realm_identifier = identifier_collection.realm_identifier
            self.realm_identifier.update(new_realm_identifier)
        elif isinstance(identifier, set):
            self.realm_identifier[realm_name].update(identifier)
        elif identifier:
            self.realm_identifier[realm_name].update([identifier])

    # yosai.core.consolidates one_by_type with by_type:
    def by_type(self, identifier_class):
        """
        returns all unique instances of a type of identifier
        :param identifier_class: the class to match identifier with
        :returns: a tuple
        """
        identifier = set()
        for identifier in self.realm_identifier.values():
            for identifier in identifier:
                if (isinstance(identifier, identifier_class)):
                    identifier.update([identifier])
        return tuple(identifier)

    def from_realm(self, realm_name):
        return self.realm_identifier.get(realm_name)

    @property
    def realm_names(self):
        return tuple(self.realm_identifier.keys())  # make immutable

    @property
    def is_empty(self):
        return (not self.realm_identifier.keys())

    def clear(self):
        self.realm_identifier = defaultdict(set)

    def __repr__(self):
        keyvals = ','.join(str(key) + '=' + str(value) for (key, value) in
                           self.realm_identifier.items())
        return "SimpleIdentifierCollection(" + keyvals + ")"

    # DG:  not clear whether a __hash__ implementation is needed in python

    # Note about serialization
    # -------------------------
    # This class was implemented using dynamic data types, for flexibility.
    # However, since a developer SHOULD know the realms that will
    # always be used, consider updating this class to a more concrete
    # implementation and consequently use a more concrete serialization schema
    @classmethod
    def serialization_schema(cls):
        class SerializationSchema(Schema):

            realm_identifier = fields.Dict(allow_none=True)

            @post_load
            def make_simple_identifier_collection(self, data):
                mycls = SimpleIdentifierCollection
                instance = mycls.__new__(mycls)
                instance.__dict__.update(data)
                return instance

            # prior to serializing, convert a dict of sets to a dict of lists
            # because sets cannot be serialized
            @post_dump
            def convert_realms(self, data):
                data['realm_identifier'] = dict(data['realm_identifier'])

                for realm, identifier in data['realm_identifier'].items():
                    data['realm_identifier'][realm] = list(identifier)
                return data

            # revert to the original dict of sets format
            @pre_load
            def revert_realms(self, data):
                olddata = copy.copy(data)
                newdata = dict(realm_identifier=defaultdict(set))

                for realm, identifier in olddata['realm_identifier'].items():
                    newdata['realm_identifier'][realm] = set(identifier)

                return newdata

        return SerializationSchema
