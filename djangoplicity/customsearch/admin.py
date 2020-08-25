# -*- coding: utf-8 -*-
#
# djangoplicity-customsearch
# Copyright (c) 2007-2014, European Southern Observatory (ESO)
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

from future import standard_library
standard_library.install_aliases()
from builtins import str
from django.conf.urls import url
from django.contrib import admin
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from djangoplicity.admincomments.admin import AdminCommentInline, \
    AdminCommentMixin
from djangoplicity.customsearch.models import CustomSearch, \
    CustomSearchCondition, CustomSearchField, CustomSearchModel, CustomSearchGroup, \
    CustomSearchLayout, CustomSearchLayoutField, CustomSearchOrdering
from djangoplicity.customsearch.tasks import export_search
from django.db import DatabaseError

try:
    from djangoplicity.contacts.models import Label
    has_labels = True
except ( ImportError, DatabaseError ):
    has_labels = False


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


class CustomSearchConditionAdmin( admin.ModelAdmin ):
    list_display = ['search', 'exclude', 'field', 'match', 'value' ]
    list_filter = ['exclude', 'match']
    list_editable = [ 'exclude', 'field', 'match', 'value' ]
    search_fields = [ 'search__name', 'field__name', 'value']
    readonly_fields = ['search']


class CustomSearchAdmin( AdminCommentMixin, admin.ModelAdmin ):
    list_display = ['name', 'model', 'group', 'admin_results_url', 'admin_export_url', 'admin_labels_url' ]
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

    def admin_labels_url( self, obj ):
        return mark_safe( """<a href="%s/labels/">Labels</a>""" % obj.pk )
    admin_labels_url.short_description = "Labels"
    admin_labels_url.allow_tags = True

    def get_urls( self ):
        urls = super( CustomSearchAdmin, self ).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        extra_urls = [
            url(r'^(?P<pk>[0-9]+)/search/$', self.admin_site.admin_view(self.search_view), name='%s_%s_search' % info),
            url(r'^(?P<pk>[0-9]+)/export/$', self.admin_site.admin_view(self.export_view), name='%s_%s_export' % info),
            url(r'^(?P<pk>[0-9]+)/labels/$', self.admin_site.admin_view(self.labels_view), name='%s_%s_labels' % info),
        ]
        return extra_urls + urls

    def _get_search_params_from_request( self, request ):
        '''
        Return the search string and ordering from request if any
        '''
        searchval = request.GET.get( "s", None )
        ordering = request.GET.get( "o", None )
        ordering_direction = request.GET.get( "ot", None )
        return (searchval, ordering, ordering_direction)

    def export_view( self, request, pk=None ):
        search = get_object_or_404( CustomSearch, pk=pk )
        s, o, ot = self._get_search_params_from_request( request )
        ( search, _qs, _searchval, _error, _header, o, ot ) = search.get_results_queryset( searchval=s, ordering=o, ordering_direction=ot )

        export_search.delay(pk, request.user.email, s, o, ot)

        return render_to_response('admin/customsearch/export.html', {'search': search, 'email': request.user.email})

    def labels_view( self, request, pk=None ):
        """
        Generate labels or show list of available labels
        """
        if not has_labels:
            return HttpResponse( "Labels generation support not available." )

        # Get queryset
        search = get_object_or_404( CustomSearch, pk=pk )
        s, o, ot = self._get_search_params_from_request( request )
        ( search, qs, searchval, error, _header, o, ot ) = search.get_results_queryset( searchval=s, ordering=o, ordering_direction=ot )

        # Get label
        try:
            label = Label.objects.get( pk=request.GET.get( 'label', None ), enabled=True )
            return label.get_label_render().render_http_response( qs, 'labels_%s.pdf' % slugify( search.name ) )
        except Label.DoesNotExist:
            # No label, so display list of available labels
            labels = Label.objects.filter( enabled=True ).order_by( 'name' )

            return render_to_response(
                "admin/customsearch/labels.html",
                {
                    'search': search,
                    'error': error,
                    'labels': labels,
                    'object_count': qs.count(),
                    'messages': [],
                    'app_label': search._meta.app_label,
                    'opts': search._meta,
                    'searchval': searchval if searchval is not None else "",
                    'has_labels': has_labels,
                },
            )

    #@permission_required( 'customsearch.can_view' )
    def search_view( self, request, pk=None ):
        """
        Perform search
        """
        search = get_object_or_404( CustomSearch, pk=pk )
        s, o, ot = self._get_search_params_from_request( request )
        ( search, qs, searchval, error, header, o, ot ) = search.get_results_queryset( searchval=s, ordering=o, ordering_direction=ot )

        # Get page num
        try:
            page = int( request.GET.get( 'p', '1' ) )
        except ValueError:
            page = 1

        try:
            paginator = Paginator( qs, 100 )

            # Adapt page to list
            try:
                objects = paginator.page( page )
            except ( EmptyPage, InvalidPage ):
                objects = paginator.page( paginator.num_pages )
        except Exception as e:
            error = str( e )
            qs = search.get_empty_queryset()
            paginator = Paginator( qs, 100 )
            objects = paginator.page( 1 )

        # Paginator params
        from urllib.parse import urlencode
        params = "&%s" % urlencode( { 'o': o, 'ot': ot } ) if o and ot else ""

        # Results header
        results_header = []
        i = 1
        for field, name, field_name in header:
            headerparams = { 'o': i, 'ot': ( 'desc' if ot == 'asc' else 'asc' ) if o == i else 'asc' }
            if searchval:
                # urlencode doesn't handle unicode, so we encode the search
                # string to utf so that it will be handled correctly
                headerparams.update( { 's': searchval.encode('utf8') } )

            results_header.append( {
                'name': name,
                'field_name': field_name,
                'sortable': field.sortable(),
                'url': mark_safe( "?%s" % urlencode( headerparams ) ),
                'class_attrib': mark_safe( 'class="sorted %s"' % ('ascending' if ot == 'asc' else 'descending' ) if o == i else ''),
            } )
            i += 1

        return render_to_response(
            "admin/customsearch/list.html",
            {
                'results_header': results_header,
                'params': mark_safe( params ),
                'search': search,
                'o': o,
                'ot': ot,
                'error': error,
                'objects': objects,
                'object_count': len( qs ),
                'data_table': search.layout.data_table( objects.object_list, quote_obj_pks=True ),
                'messages': [],
                'app_label': search._meta.app_label,
                'opts': search._meta,
                'reverse_name': "admin:%s_%s_change" % ( qs.model._meta.app_label, qs.model._meta.model_name ),
                'searchval': searchval if searchval is not None else "",
                'has_labels': has_labels,
            },
        )


def register_with_admin( admin_site ):
    admin_site.register( CustomSearch, CustomSearchAdmin )
    admin_site.register( CustomSearchModel, CustomSearchModelAdmin )
    admin_site.register( CustomSearchGroup, CustomSearchGroupAdmin )
    admin_site.register( CustomSearchLayout, CustomSearchLayoutAdmin )
    admin_site.register( CustomSearchCondition, CustomSearchConditionAdmin )


# Register with default admin site
register_with_admin( admin.site )
