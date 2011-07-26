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

MATCH_TYPE = (
	('__exact','Exact'),
	('__contains','Contains'),
	('__startswith','Starts with'),
	('__endswith','Ends with'),
	('__regex','Regular expression'),
	('__iexact','Exact (case-insensitive)'),
	('__icontains','Contains (case-insensitive)'),
	('__istartswith','Starts with (case-insensitive)'),
	('__iendswith','Ends with (case-insensitive)'),
	('__iregex','Regular expression (case-insensitive)'),
)

class CustomSearchGroup( models.Model ):
	"""
	Groups for custom searches
	"""
	name = models.CharField( max_length=255, blank=True )
	
	def __unicode__(self):
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
	
	def full_field_name( self ):
		return "%s%s" % ( self.field_name, self.selector )

	
	def clean(self):
		if self.selector != "" and not self.selector.startswith( "__" ):
			raise ValidationError( "Selector must start with two underscores" )
	
	def __unicode__( self ):
		return "%s: %s" % ( self.model.name, self.name,  )


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
		for f in self.fields.all():
			header += self._get_header_value( f )
		return header
	

	def rows( self, query_set ):
		"""
		"""
		data = []
		
		for obj in query_set:
			row = []
			for f in self.fields.all():
				row += self._get_field_value( obj, f )
			data.append( row )

		return data
	
	def _get_field_value( self, obj, field ):
		modelcls = self.model.model.model_class()
		( field_object, m, direct, m2m ) = modelcls._meta.get_field_by_name( field.field_name )
		
		if not m2m:
			return [getattr( obj, field.fiel_name )]
		else:
			return ["; ".join( getattr( obj, field.fiel_name ).all() ) ]

	
	def _get_header_value(self, field ):
		return [( field.name, field.field_name )]
#		modelcls = self.model.model.model_class()
#		
#		( field_object, m, direct, m2m ) = modelcls._meta.get_field_by_name( field.field_name )
#		
#		if not m2m:
#			return [( field.name, field.field_name )]
#		else:
#			if direct:
#				cols = []
#				for v in field_object.related.parent_model.objects.all():
#					cols.append( ( "%s: %s" % ( field.name, unicode( v ) ) , "%s:%s" % ( field.field_name, v.pk ) ) )
#					
#				return cols				
#		return []
	
	def __unicode__( self ):
		return "%s: %s" % ( self.model.name, self.name, )


class CustomSearchLayoutField( models.Model ):
	layout = models.ForeignKey( CustomSearchLayout )
	field = models.ForeignKey( CustomSearchField )
	position = models.PositiveIntegerField( null=True, blank=True )
	
	def clean( self ):
		if self.layout.model != self.field.model:
			raise ValidationError( 'Field %s does not belong to %s' % ( self.field, self.layout.model.name ) )


	
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
		permissions = (
			( "can_view", "Can view all custom searches" )
		)
		
	def clean( self ):
		"""
		Ensure the layout model matches the search model.
		"""
		if self.model != self.layout.model:
			raise ValidationError( 'Layout %s does not belong to %s' % ( self.layout, self.model.name ) )

	def get_query_set(self):
		"""
		Execute the custom search
		"""
		include = {}
		exclude = {}
		
		# Collect all search conditions
		for c in self.customsearchcondition_set.filter( field__model=self.model ):
			tmp = exclude if c.exclude else include

			if c.field.field_name not in tmp:
				tmp[c.field.field_name] = []
			tmp[c.field.field_name].append( ( c.value, c.match ) )

		# Create Q objects for all conditions
		include_queries = []
		exclude_queries = []
		
		for field,values in include.items():
			include_queries.append( reduce( operator.or_, [models.Q( **{ "%s%s" % (field,match) : val } ) for (val,match) in values] )  )
			
		for field,values in exclude.items():
			exclude_queries.append( reduce( operator.or_, [models.Q( **{ "%s%s" % (field,match) : val } ) for (val,match) in values] )  )
				
		include_queries = reduce( operator.and_, include_queries ) if len( include_queries ) > 1 else include_queries
		exclude_queries = reduce( operator.and_, exclude_queries ) if len( exclude_queries ) > 1 else None
		
		# Generate queryset for search.
		qs = self.model.model_class().objects.all()
		if include_queries:
			qs = qs.filter( include_queries )
		if exclude_queries:
			qs = qs.exclude( exclude_queries )
		
		return qs

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
	field = models.ForeignKey( CustomSearchField )
	match = models.CharField( max_length=30, choices=MATCH_TYPE )
	value = models.CharField( max_length=255, blank=True )
	
	def clean( self ):
		"""
		Ensure the field model matches the search model.
		"""
		from django.core.exceptions import ValidationError
		
		if self.field.model != self.search.model:
			raise ValidationError( 'Field %s does not belong to %s' % (self.field, self.search.model.name) )

	

