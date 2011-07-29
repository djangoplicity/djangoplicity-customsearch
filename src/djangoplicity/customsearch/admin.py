# -*- coding: utf-8 -*-
#
# djangoplicity-customsearch
# Copyright (c) 2007-2011, European Southern Observatory (ESO)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the European Southern Observatory nor the names 
#      of its contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
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

from django import forms
from django.conf.urls.defaults import patterns
from django.contrib import admin
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from djangoplicity.admincomments.admin import AdminCommentInline, \
	AdminCommentMixin
from djangoplicity.customsearch.models import CustomSearch, \
	CustomSearchCondition, CustomSearchField, CustomSearchModel, CustomSearchGroup, \
	CustomSearchLayout, CustomSearchLayoutField, CustomSearchOrdering

class CustomSearchFieldInlineAdmin( admin.TabularInline ):
	model = CustomSearchField
	extra = 3


class CustomSearchConditionInlineAdmin( admin.TabularInline ):
	model = CustomSearchCondition
	extra = 3
	
class CustomSearchOrderingInlineAdmin( admin.TabularInline ):
	model = CustomSearchOrdering
	extra = 1
	
class CustomSearchLayoutFieldInlineAdmin( admin.TabularInline ):
	model = CustomSearchLayoutField
	extra = 3

class CustomSearchModelAdmin( admin.ModelAdmin ):
	list_display = ['name', 'model', 'app' ]
	search_fields = ['name', ]
	inlines = [ CustomSearchFieldInlineAdmin ]
	
	def app( self, obj ):
		return obj.model.app_label


class CustomSearchLayoutAdmin( admin.ModelAdmin ):
	list_display = ['name', 'model', ]
	search_fields = ['name', ]
	inlines = [ CustomSearchLayoutFieldInlineAdmin ]


class CustomSearchGroupAdmin( admin.ModelAdmin ):
	list_display = ['name', ]
	search_fields = ['name', ]

class CustomSearchAdmin( AdminCommentMixin, admin.ModelAdmin ):
	list_display = ['name', 'model', 'group', 'admin_results_url', 'admin_export_url' ]
	list_filter = ['model', 'group' ]
	search_fields = ['name', 'model__name' ]
	fieldsets = ( 
		( None, {
			'fields': ( 'name', 'model', 'layout', 'group', )
		} ),
		( 'Description', {
			'fields': ( 'human_readable_text', )
		} ),
	)
	inlines = [ CustomSearchConditionInlineAdmin, CustomSearchOrderingInlineAdmin, AdminCommentInline ]
	readonly_fields = ['human_readable_text']
	
	def admin_results_url( self, obj ):
		return mark_safe( """<a href="%s/search/">Results</a>""" % obj.pk )
	admin_results_url.short_description = "Results"
	admin_results_url.allow_tags = True
	
	def admin_export_url( self, obj ):
		return mark_safe( """<a href="%s/export/">Export</a>""" % obj.pk )
	admin_export_url.short_description = "Export"
	admin_export_url.allow_tags = True
	
	def get_urls( self ):
		urls = super( CustomSearchAdmin, self ).get_urls()
		extra_urls = patterns( '',
			( r'^(?P<pk>[0-9]+)/search/$', self.admin_site.admin_view( self.search_view ) ),
			( r'^(?P<pk>[0-9]+)/export/$', self.admin_site.admin_view( self.export_view ) ),
		)
		return extra_urls + urls
	
	def export_view( self, request, pk=None ):
		return HttpResponse("Not yet supported.")

	def search_view( self, request, pk=None ):
		"""
		Perform search
		"""
		search = get_object_or_404( CustomSearch, pk=pk )
		
		# Search
		searchval = request.GET.get( "s", None )
		
		# Get page num
		try:
			page = int( request.GET.get( 'p', '1' ) )
		except ValueError:
			page = 1

		paginator = Paginator( search.get_query_set( freetext=searchval ), 100 )
		
		# Adapt page to list
		try:
			objects = paginator.page( page )
		except ( EmptyPage, InvalidPage ):
			objects = paginator.page( paginator.num_pages )
			
		return render_to_response( 
			"admin/customsearch/list.html", 
			{
				'search' : search,
				'objects' : objects,
				'data_table' : search.layout.data_table( objects.object_list ), 
				'messages': [],
				'app_label' : search._meta.app_label,
				'opts' : search._meta,
				'searchval' : searchval,
				
			}, 
			context_instance=RequestContext( request ) 
		)

		


def register_with_admin( admin_site ):
	admin_site.register( CustomSearch, CustomSearchAdmin )
	admin_site.register( CustomSearchModel, CustomSearchModelAdmin )
	admin_site.register( CustomSearchGroup, CustomSearchGroupAdmin )
	admin_site.register( CustomSearchLayout, CustomSearchLayoutAdmin )
		
# Register with default admin site	
register_with_admin( admin.site )