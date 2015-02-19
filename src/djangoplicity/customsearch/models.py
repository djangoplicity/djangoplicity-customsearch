# -*- coding: utf-8 -*-
#
# djangoplicity-customsearch
# Copyright (c) 2007-2011, European Southern Observatory (ESO)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#	* Redistributions of source code must retain the above copyright
#	  notice, this list of conditions and the following disclaimer.
#
#	* Redistributions in binary form must reproduce the above copyright
#	  notice, this list of conditions and the following disclaimer in the
#	  documentation and/or other materials provided with the distribution.
#
#	* Neither the name of the European Southern Observatory nor the names
#	  of its contributors may be used to endorse or promote products derived
#	  from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY ESO ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL ESO BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE
#

"""
This custom search application allows admin users to create ad-hoc queries into
nearly any django model, using a subset of the django queryset API.

An super user must initially specify the models and fields that can be search on. Once
that is done, any admin user can make queries as they like.

The search results can either be browsed ( and search with freetext), exported or
used for e.g. label generation if djangoplicity-contacts is installed.
"""


from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.util import quote
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.aggregates import Max, Min
from django.db.models.fields import FieldDoesNotExist
from django.db.models.related import RelatedObject
from datetime import datetime
import operator

MATCH_TYPE = (
	( '__exact', 'Exact' ),
	( '__contains', 'Contains' ),
	( '__startswith', 'Starts with' ),
	( '__endswith', 'Ends with' ),
	( '__regex', 'Regular expression' ),
	( '__iexact', 'Exact (case-insensitive)' ),
	( '__icontains', 'Contains (case-insensitive)' ),
	( '__istartswith', 'Starts with (case-insensitive)' ),
	( '__iendswith', 'Ends with (case-insensitive)' ),
	( '__iregex', 'Regular expression (case-insensitive)' ),
	( '__year', 'Year' ),
	( '__month', 'Month' ),
	( '__day', 'Day' ),
	( '__week_day', 'Week day' ),
	( '__gt', 'Greater than' ),
	( '__gte', 'Greater than or equal to' ),
	( '__lt', 'Less than' ),
	( '__lte', 'Less than or equal to' ),
	( '__isnull', 'Is null' ),
	( '__gt', 'After' ),
	( '__lte', 'Before' ),
)
# List of allowed field loookup types


class CustomSearchGroup( models.Model ):
	"""
	Groups for custom searches
	"""
	name = models.CharField( max_length=255, blank=True )

	def __unicode__( self ):
		return self.name


class CustomSearchModel( models.Model ):
	"""
	Define which models you can search on.
	"""
	name = models.CharField( max_length=255 )
	model = models.ForeignKey( ContentType )

	def __unicode__( self ):
		return self.name


class CustomSearchField( models.Model ):
	"""
	Define a field for a custom search model
	"""
	model = models.ForeignKey( CustomSearchModel )
	name = models.CharField( max_length=255 )
	field_name = models.SlugField()
	selector = models.SlugField( blank=True )
	sort_selector = models.SlugField( blank=True )
	enable_layout = models.BooleanField( default=True )
	enable_search = models.BooleanField( default=True )
	enable_freetext = models.BooleanField( default=True )

	def full_field_name( self ):
		return str( "%s%s" % ( self.field_name, self.selector ) )

	def sort_field_name( self ):
		return str( "%s%s" % ( self.field_name, self.sort_selector if self.sort_selector else self.selector ) )

	def get_modelclass_field( self ):
		return self.model.model.model_class()._meta.get_field_by_name( self.field_name )

	def sortable( self ):
		return True

	def clean( self ):
		if self.selector != "" and not self.selector.startswith( "__" ):
			raise ValidationError( "Selector must start with two underscores" )

	def __unicode__( self ):
		return "%s: %s" % ( self.model.name, self.name, )

	class Meta:
		ordering = ['model__name', 'name']


class CustomSearchLayout( models.Model ):
	"""
	"""
	model = models.ForeignKey( CustomSearchModel )
	name = models.CharField( max_length=255 )
	fields = models.ManyToManyField( CustomSearchField, through='CustomSearchLayoutField' )

	def header( self ):
		"""
		"""
		header = []
		for f in CustomSearchLayoutField.objects.filter( layout=self ).select_related():
			header += self._get_header_value( f.field, expand=f.expand_rel )
		return header

	def data_table( self, queryset, quote_obj_pks=False ):
		"""
		"""
		data = []
		layout_qs = CustomSearchLayoutField.objects.filter( layout=self ).select_related()

		for obj in queryset:
			row = []
			for f in layout_qs:
				row += self._get_field_value( obj, f.field, expand=f.expand_rel )
			data.append( { 'object': obj, 'values': row, 'object_pk': quote(obj.pk) if quote_obj_pks else obj.pk} )

		return data

	def _get_field_value( self, obj, field, expand=False ):
		modelcls = self.model.model.model_class()
		try:
			( field_object, m, direct, m2m ) = modelcls._meta.get_field_by_name( field.field_name )
		except FieldDoesNotExist:
			# The field is most likely a property()
			return [getattr(obj, field.field_name)]

		# Get accessor value
		accessor = field.field_name
		if isinstance( field_object, RelatedObject ):
			m2m = True
			accessor = field_object.get_accessor_name()

		if m2m and expand:
			rels = getattr( obj, accessor ).all()

			cols = []
			for v in field_object.related.parent_model.objects.all():
				if v in rels:
					cols.append( "X" )
				else:
					cols.append( "" )
			return cols
		elif m2m and not expand:
			tmp = "\";\"".join( [unicode( x ).replace( '"', '""' ) for x in getattr( obj, accessor ).all()] )
			return [ '"%s"' % tmp if tmp else "" ]
		else:
			result = getattr( obj, accessor )
			if expand and field.selector.startswith('__'):
				result = getattr( result, field.selector.split('__')[1] )
			return [result]

	def _get_header_value( self, field, expand=False ):
		modelcls = self.model.model.model_class()
		try:
			( field_object, m, direct, m2m ) = modelcls._meta.get_field_by_name( field.field_name )
		except FieldDoesNotExist:
			# The field is most likely a property()
			return [(field, field.name, field.field_name)]

		if m2m and expand:
			if direct:
				cols = []
				for v in field_object.related.parent_model.objects.all():
					cols.append( ( field, "%s: %s" % ( field.name, unicode( v ) ), "%s:%s" % ( field.field_name, v.pk ) ) )
				return cols
		else:
			return [( field, field.name, field.field_name )]

	def __unicode__( self ):
		return "%s: %s" % ( self.model.name, self.name, )


class CustomSearchLayoutField( models.Model ):
	layout = models.ForeignKey( CustomSearchLayout )
	field = models.ForeignKey( CustomSearchField, limit_choices_to={ 'enable_layout': True } )
	position = models.PositiveIntegerField( null=True, blank=True )
	expand_rel = models.BooleanField( default=False )

	def clean( self ):
		if self.layout.model != self.field.model:
			raise ValidationError( 'Field %s does not belong to %s' % ( self.field, self.layout.model.name ) )
		if not self.field.enable_layout:
			raise ValidationError( 'Field %s does not allow use in layout' % self.field )

	class Meta:
		ordering = ['position', 'id']


class CustomSearch( models.Model ):
	"""
	Model for defining a custom search on the contact model
	"""
	name = models.CharField( max_length=255 )
	model = models.ForeignKey( CustomSearchModel )
	group = models.ForeignKey( CustomSearchGroup, blank=True, null=True )
	layout = models.ForeignKey( CustomSearchLayout )

	class Meta:
		verbose_name_plural = 'custom searches'
		permissions = [
			( "can_view", "Can view all custom searches" ),
		]
		ordering = ['name']

	def __unicode__( self ):
		return self.name

	def human_readable_text( self ):
		"""
		Make a human readable text describing this search.
		"""
		text = []
		include, exclude = self._collect_search_conds()
		match_types = dict( MATCH_TYPE )

		for conditions, title in [( include, 'Include' ), ( exclude, 'Exclude' )]:
			field_texts = []
			for field, values in conditions.items():
				field_title = field.name.lower()

				# Group values for each match type
				field_match = {}
				for match, val in values:
					if match not in field_match:
						field_match[match] = []
					field_match[match].append(val)

				match_texts = []
				for match, values in field_match.items():
					if match == '__exact':
						match_title = "matches"
					elif match == '__iexact':
						match_title = "matches (case-insensitive)"
					elif match == '__regex':
						match_title = "matches regular expression"
					elif match == '__iregex':
						match_title = "matches regular expression (case-insensitive)"
					elif match in ['__year', '__month', '__day', "__week_day"]:
						match_title = "%s is" % match_types[match].lower()
					elif match in ['__gt', '__gte', '__lt', "__lte"]:
						match_title = "is %s" % match_types[match].lower()
					else:
						match_title = match_types[match].lower()

					if match == "__isnull" and True in values:
						match_texts.append( "is null" )
					elif match == "__isnull" and False in values:
						match_texts.append( "is not null" )
					else:
						match_texts.append( "%s %s" % ( match_title, " or ".join( ['"%s"' % x for x in values] ) ) )
				field_texts.append( "%s %s" % ( field_title, " or ".join( match_texts ) ) )

			if field_texts:
				text.append("%s %s where %s." % ( title, self.model.model.model_class()._meta.verbose_name_plural.lower(), " and, ".join( field_texts ) ))

		ordering = self.customsearchordering_set.all()
		if len(ordering) > 0:
			text.append("Order result by %s." % ", ".join( [o.field.name.lower() for o in ordering] ) )

		return " ".join( text ) if text else "Include all %s." % self.model.model.model_class()._meta.verbose_name_plural.lower()

	def clean( self ):
		"""
		Ensure the layout model matches the search model.
		"""
		if self.model != self.layout.model:
			raise ValidationError( 'Layout %s does not belong to %s' % ( self.layout, self.model.name ) )

	def _collect_search_conds( self ):
		include = {}
		exclude = {}

		for c in self.customsearchcondition_set.filter( field__model=self.model ).select_related():
			tmp = exclude if c.exclude else include

			if c.field not in tmp:
				tmp[c.field] = []
			tmp[c.field].append( ( c.match, c.prepared_value() ) )

		return ( include, exclude )

	def get_empty_queryset( self ):
		modelclass = self.model.model.model_class()
		return modelclass.objects.none()

	def get_results_queryset( self, searchval=None, ordering=None, ordering_direction=None, evaluate=True ):
		"""
		Get the queryset for the selected custom search.
		"""
		header = self.layout.header()

		search_ordering = None

		try:
			if ordering_direction not in ['asc', 'desc']:
				ordering_direction = 'asc'

			ordering = int( ordering )
			if ordering <= 0:
				raise ValueError
			( field, name, field_name ) = header[ordering - 1]
			if field.sortable():
				search_ordering = [ CustomSearchOrdering( field=field, descending=( ordering_direction == 'desc' ) ) ]
		except ( ValueError, IndexError, TypeError ):
			ordering = None
			ordering_direction = None

		qs = self.get_queryset( freetext=searchval, override_ordering=search_ordering )

		if evaluate:
			try:
				qs.count()
				error = ""
			except Exception, e:
				error = unicode( e )
				qs = self.get_empty_queryset()
		else:
			error = ""

		return ( self, qs, searchval, error, header, ordering, ordering_direction )

	def get_queryset( self, freetext=None, override_ordering=None ):
		"""
		Execute the custom search
		"""
		# Collect all search conditions
		include, exclude = self._collect_search_conds()

		# Create Q objects for all conditions
		include_queries = []
		exclude_queries = []

		for field, values in include.items():
			include_queries.append( reduce( operator.or_, [models.Q( **{ str("%s%s" % ( field.full_field_name(), match )): val } ) for ( match, val ) in values] ) )

		for field, values in exclude.items():
			# Identical to include queries except that the Q object is negated with ~ and all qs are and'ed together
			exclude_queries.append( reduce( operator.and_, [~models.Q( **{ str("%s%s" % ( field.full_field_name(), match )): val } ) for ( match, val ) in values] ) )

		# Generate queryset for search.
		modelclass = self.model.model.model_class()
		qs = modelclass.objects.all()
		if include_queries or exclude_queries:
			qs = qs.filter( *( include_queries + exclude_queries ) )

		# Free text search in result set
		if freetext:
			qobjects = []
			for f in CustomSearchField.objects.filter( model=self.model, enable_freetext=True ):
				arg = "%s__icontains" % f.full_field_name()
				qobjects.append( models.Q( **{ str( arg ): freetext } ) )
			qs = qs.filter( reduce( operator.or_, qobjects ) )
		qs = qs.distinct()

		# Ordering
		# ========
		# NOTE: distinct() and order_by() does not work well together (https://docs.djangoproject.com/en/1.3/ref/models/querysets/#distinct).
		# If you order by a related field (e.g. groups__name) then groups__name is included in the SELECT columns (e.g SELECT first_name, ..., contact_groups.name).
		# This means that distinct() method (akak SELECT DISTINCT) will no longer be able to detect duplicate Contact objects
		#
		# The work around is to either annotate each Model object with the value you want to order by, or add an extra attribute
		# on the Model you want to order (see e.g. http://archlinux.me/dusty/2010/12/07/django-dont-use-distinct-and-order_by-across-relations/)
		if override_ordering is None:
			ordering = self.customsearchordering_set.all().select_related( 'field' )
		else:
			ordering = override_ordering

		if len( ordering ) > 0:
			for o in ordering:
				qs = o.annotate_qs( qs )
			qs = qs.order_by( *[o.order_by_field() for o in ordering] )

		return qs

	def get_data_table( self ):
		return self.layout.rows( self.get_queryset() )


class CustomSearchCondition( models.Model ):
	"""
	Represents one condition for a custom search. A condition can
	either be an include or exclude condition. Basically, include
	conditions are passed to the QuerySet filter() method, and exclude
	statements are  passed to the QuyerSet exclude() method. Each
	condition have the following matches:
	"""
	number_lookups = ['__year', '__month', '__day', '__weekday', ]
	boolean_lookups = ['__isnull', ]
	date_lookups = ['__gt', '__lte']

	search = models.ForeignKey( CustomSearch )
	exclude = models.BooleanField( default=False )
	field = models.ForeignKey( CustomSearchField, limit_choices_to={ 'enable_search': True } )
	match = models.CharField( max_length=30, choices=MATCH_TYPE )
	value = models.CharField( max_length=255, blank=True )

	def prepared_value( self ):
		"""
		Prepare value from string representation.
		"""
		if self.match in self.date_lookups and self.value == 'now()':
			return datetime.now()
		if self.match in self.number_lookups:
			try:
				return int( self.value )
			except ValueError:
				raise ValidationError("Value is not an integer.")
		elif self.match in self.boolean_lookups:
			if self.value.strip().lower() == "false":
				return False
			elif self.value.strip().lower() == "true":
				return True
			else:
				raise ValidationError("Value is not a truth value.")
		else:
			return self.value

	def check_value( self ):
		"""
		Check if value is valid for the given match type.
		"""
		if self.match in self.number_lookups:
			try:
				int( self.value )
			except ValueError:
				raise ValidationError( "Value must be an integer for match type '%s'." % self.get_match_display() )
		elif self.match in self.boolean_lookups:
			if self.value.strip().lower() not in ['true', 'false']:
				raise ValidationError("Value must be either true or false for match type '%s'." % self.get_match_display() )

	def clean( self ):
		"""
		Ensure the field model matches the search model.
		"""
		self.check_value()

		if self.field.model != self.search.model:
			raise ValidationError( 'Field %s does not belong to %s' % ( self.field, self.search.model.name ) )

		if not self.field.enable_search:
			raise ValidationError( 'Field %s does not allow searching' % self.field )


class CustomSearchOrdering( models.Model ):
	"""
	Allow ordering of fields
	"""
	search = models.ForeignKey( CustomSearch )
	field = models.ForeignKey( CustomSearchField, limit_choices_to={ 'enable_search': True } )
	descending = models.BooleanField( default=False )

	def order_by_field( self ):
		"""
		"""
		sort_field = self.field.sort_field_name()

		if self.field.sort_selector:
			order_by = '-%s__max' % sort_field if self.descending else '%s__min' % sort_field
		else:
			order_by = '-%s' % sort_field if self.descending else sort_field

		return order_by

	def annotate_qs( self, qs ):
		"""
		"""
		if self.field.sort_selector:
			if self.descending:
				qs = qs.annotate( **{ str('%s__max' % self.field.sort_field_name() ): Max( self.field.sort_field_name() ) } )
			else:
				qs = qs.annotate( **{ str('%s__min' % self.field.sort_field_name() ): Min( self.field.sort_field_name() ) } )

		return qs

	def clean( self ):
		"""
		Ensure the field model matches the search model.
		"""
		if self.field.model != self.search.model:
			raise ValidationError( 'Field %s does not belong to %s' % ( self.field, self.search.model.name ) )

		if not self.field.enable_search:
			raise ValidationError( 'Field %s does not allow ordering' % self.field )
