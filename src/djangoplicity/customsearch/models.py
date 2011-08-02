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


from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
import operator
from django.core.exceptions import ValidationError
from django.db.models.related import RelatedObject

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
 )

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
	enable_layout = models.BooleanField( default=True )
	enable_search = models.BooleanField( default=True ) 

	def full_field_name( self ):
		return "%s%s" % ( self.field_name, self.selector )
	
	def get_modelclass_field( self ):
		return self.model.model.model_class()._meta.get_field_by_name( self.field_name )

	def clean( self ):
		if self.selector != "" and not self.selector.startswith( "__" ):
			raise ValidationError( "Selector must start with two underscores" )

	def __unicode__( self ):
		return "%s: %s" % ( self.model.name, self.name, )


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

	def data_table( self, query_set ):
		"""
		"""
		data = []

		for obj in query_set:
			row = []
			for f in CustomSearchLayoutField.objects.filter( layout=self ).select_related():
				row += self._get_field_value( obj, f.field, expand=f.expand_rel )
			data.append( { 'object' : obj, 'values' : row } )
		
		return data

	def _get_field_value( self, obj, field, expand=False ):
		modelcls = self.model.model.model_class()
		( field_object, m, direct, m2m ) = modelcls._meta.get_field_by_name( field.field_name )
		
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
			return [getattr( obj, accessor )]
			


	def _get_header_value( self, field, expand=False ):
		modelcls = self.model.model.model_class()
		( field_object, m, direct, m2m ) = modelcls._meta.get_field_by_name( field.field_name )
			
		if m2m and expand:
			if direct:
				cols = []
				for v in field_object.related.parent_model.objects.all():
					cols.append( ( "%s: %s" % ( field.name, unicode( v ) ) , "%s:%s" % ( field.field_name, v.pk ) ) )
				return cols
		else:
			return [( field.name, field.field_name )]
		
		
	

	def __unicode__( self ):
		return "%s: %s" % ( self.model.name, self.name, )


class CustomSearchLayoutField( models.Model ):
	layout = models.ForeignKey( CustomSearchLayout )
	field = models.ForeignKey( CustomSearchField, limit_choices_to={ 'enable_layout' : True } )
	position = models.PositiveIntegerField( null=True, blank=True )
	expand_rel = models.BooleanField( default=False )

	def clean( self ):
		if self.layout.model != self.field.model:
			raise ValidationError( 'Field %s does not belong to %s' % ( self.field, self.layout.model.name ) )
		if not self.field.enable_layout:
			raise ValidationError( 'Field %s does not allow use in layout' % self.field )



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
		
	def __unicode__( self ):
		return self.name


	def human_readable_text( self ):
		"""
		Make a human readable text describing this search.
		"""
		text = []
		include,exclude = self._collect_search_conds()
		match_types = dict( MATCH_TYPE )
		
		for conditions,title in [( include, 'Include' ), ( exclude, 'Exclude' )]:
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
					else:
						match_title = match_types[match].lower()
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

		for c in self.customsearchcondition_set.filter( field__model=self.model ):
			tmp = exclude if c.exclude else include

			if c.field not in tmp:
				tmp[c.field] = []
			tmp[c.field].append( ( c.match, c.value ) )

		return ( include, exclude )

	def get_query_set( self, freetext=None ):
		"""
		Execute the custom search
		"""
		# Collect all search conditions
		include, exclude = self._collect_search_conds()

		# Create Q objects for all conditions
		include_queries = []
		exclude_queries = []

		for field, values in include.items():
			include_queries.append( reduce( operator.or_, [models.Q( **{ str("%s%s" % ( field.full_field_name(), match )) : val } ) for ( match, val ) in values] ) )

		for field, values in exclude.items():
			exclude_queries.append( reduce( operator.or_, [models.Q( **{ str("%s%s" % ( field.full_field_name(), match )) : val } ) for ( match, val ) in values] ) )

		include_queries = reduce( operator.and_, include_queries ) if len( include_queries ) > 0 else None
		exclude_queries = reduce( operator.and_, exclude_queries ) if len( exclude_queries ) > 0 else None

		# Generate queryset for search.
		modelclass = self.model.model.model_class()
		qs = modelclass.objects.all()
		if include_queries:
			qs = qs.filter( include_queries )
		if exclude_queries:
			qs = qs.exclude( exclude_queries )
		
		
		# Free text search in result set
		if freetext:
			qobjects = []
			for f in CustomSearchField.objects.filter( model=self.model, enable_search=True ):
				arg = "%s__icontains" % f.full_field_name()
				qobjects.append( models.Q( **{ str(arg) : freetext } ) )
			qs = qs.filter( reduce( operator.or_, qobjects ) ).distinct()	
			
		# Ordering
		ordering = self.customsearchordering_set.all()
		if len(ordering) > 0:
			qs.order_by( *["%s%s" % ( "-" if o.descending else "", o.field.full_field_name() ) for o in ordering] )

		return qs
	
	def get_data_table( self ):
		return self.layout.rows( self.get_query_set() )



class CustomSearchCondition( models.Model ):
	"""
	Represents one condition for a custom search. A condition can
	either be an include or exclude condition. Basically, include
	conditions are passed to the QuerySet filter() method, and exclude
	statements are  passed to the QuyerSet exclude() method. Each 
	condition have the following matches:
	"""
	search = models.ForeignKey( CustomSearch )
	exclude = models.BooleanField( default=False )
	field = models.ForeignKey( CustomSearchField, limit_choices_to={ 'enable_search' : True } )
	match = models.CharField( max_length=30, choices=MATCH_TYPE )
	value = models.CharField( max_length=255, blank=True )

	def clean( self ):
		"""
		Ensure the field model matches the search model.
		"""
		from django.core.exceptions import ValidationError

		if self.field.model != self.search.model:
			raise ValidationError( 'Field %s does not belong to %s' % ( self.field, self.search.model.name ) )
		
		if not self.field.enable_search:
			raise ValidationError( 'Field %s does not allow searching' % self.field )
		

class CustomSearchOrdering( models.Model ):
	"""
	Allow ordering of fields
	"""
	search = models.ForeignKey( CustomSearch )
	field = models.ForeignKey( CustomSearchField, limit_choices_to={ 'enable_search' : True } )
	descending = models.BooleanField( default=False )

	def clean( self ):
		"""
		Ensure the field model matches the search model.
		"""
		from django.core.exceptions import ValidationError

		if self.field.model != self.search.model:
			raise ValidationError( 'Field %s does not belong to %s' % ( self.field, self.search.model.name ) )
		
		if not self.field.enable_search:
			raise ValidationError( 'Field %s does not allow ordering' % self.field )



