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
from django.contrib import admin
from django.utils.translation import ugettext as _
from djangoplicity.admincomments.admin import AdminCommentInline, \
	AdminCommentMixin
from djangoplicity.customsearch.models import CustomSearch, \
	CustomSearchCondition, CustomSearchField, CustomSearchModel, CustomSearchGroup, \
	CustomSearchLayout, CustomSearchLayoutField

class CustomSearchFieldInlineAdmin( admin.TabularInline ):
	model = CustomSearchField
	extra = 3


class CustomSearchConditionInlineAdmin( admin.TabularInline ):
	model = CustomSearchCondition
	extra = 3
	
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
	list_display = ['name', 'model', 'group' ]
	list_filter = ['model', 'group' ]
	search_fields = ['name', 'model__name' ]
	inlines = [ CustomSearchConditionInlineAdmin, AdminCommentInline ]


def register_with_admin( admin_site ):
	admin_site.register( CustomSearch, CustomSearchAdmin )
	admin_site.register( CustomSearchModel, CustomSearchModelAdmin )
	admin_site.register( CustomSearchGroup, CustomSearchGroupAdmin )
	admin_site.register( CustomSearchLayout, CustomSearchLayoutAdmin )
		
# Register with default admin site	
register_with_admin( admin.site )