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

from djangoplicity.customsearch.exporter import ExcelExporter
from djangoplicity.customsearch.models import CustomSearch

from celery.task import task
from django.core.mail import EmailMessage
from tempfile import NamedTemporaryFile
import os


@task
def export_search(search_id, email, searchval=None, ordering=None, ordering_direction=None):
	'''
	Export a given search to file and email to the given address
	'''
	search = CustomSearch.objects.get(pk=search_id)

	# Rename the / from the search name if any
	prefix = search.name.replace('/', '-')

	# Generate a temporary file
	f = NamedTemporaryFile(prefix=prefix + '-', suffix='.xls', delete=False)

	(search, qs, searchval, error, header, o, ot) = search.get_results_queryset(
			searchval=searchval,
			ordering=ordering,
			ordering_direction=ordering_direction)

	exporter = ExcelExporter(f, header=[ (x[1], None) for x in header ])

	for row in search.layout.data_table(qs):
		exporter.writerow(row['values'])
	exporter.save(f)
	f.close()

	# Send the export file as attachment
	email = EmailMessage('Custom Search export ready: "%s"' % search.name,
				'', 'no-reply@eso.org', [email])
	email.attach_file(f.name)
	email.send()

	# Remove the temporary file
	os.remove(f.name)
