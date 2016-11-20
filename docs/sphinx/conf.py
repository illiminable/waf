# -*- coding: utf-8 -*-
#
# waf documentation build configuration file, created by
# sphinx-quickstart on Sat Nov  6 20:46:09 2010.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys, os, re

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath(os.path.join('..', "..")))
sys.path.append(os.path.abspath('.'))

graphviz_output_format = 'svg'

# monkey patch a few waf classes for documentation purposes!
#-----------------------------------------------------------

from waflib import TaskGen
from waflib.TaskGen import task_gen, feats

exclude_taskgen = []
def taskgen_method(func):
	exclude_taskgen.append(func.__name__)
	setattr(task_gen, func.__name__, func)
	fix_fun_doc(func)
	return func
taskgen_method.__doc__ = TaskGen.taskgen_method.__doc__
TaskGen.taskgen_method = taskgen_method

def extension(*k):
	def deco(func):
		exclude_taskgen.append(func.__name__)
		setattr(task_gen, func.__name__, func)
		for x in k:
			task_gen.mappings[x] = func
		return func
	return deco
extension.__doc__ = TaskGen.extension.__doc__
TaskGen.extension = extension

def fix_fun_doc(fun):
	try:
		if not fun.__doc__.startswith('\tTask generator method'):
			fun.__doc__ = '\tTask generator method\n\t\n' + (fun.__doc__ or '')
	except Exception as e:
		print("Undocumented function %r (%r)" % (fun.__name__, e))
		fun.__doc__ = ""

def fixmeth(x):
	if x == 'process_source':
		return ":py:func:`waflib.TaskGen.process_source`"
	if x == 'process_rule':
		return ":py:func:`waflib.TaskGen.process_rule`"
	return ":py:func:`%s`" % x

def fixfeat(x):
	app = '../'
	if x in ('*', 'subst'):
		app = ''
	return "`%s <%sfeaturemap.html#feature%s>`_" % (x=='*' and 'all' or x, app, x!='*' and '-'+x or '')

def append_doc(fun, keyword, meths):

	if keyword == "feature":
		meths = [fixfeat(x) for x in meths]
	else:
		meths = [fixmeth(x) for x in meths]

	dc = ", ".join(meths)
	fun.__doc__ += '\n\t:%s: %s' % (keyword, dc)

def feature(*k):
	def deco(func):
		exclude_taskgen.append(func.__name__)
		setattr(task_gen, func.__name__, func)
		for name in k:
			feats[name].update([func.__name__])
		fix_fun_doc(func)
		append_doc(func, 'feature', k)
		#print "feature", name, k
		return func
	return deco
feature.__doc__ = TaskGen.feature.__doc__
TaskGen.feature = feature


def before(*k):
	def deco(func):
		exclude_taskgen.append(func.__name__)
		setattr(task_gen, func.__name__, func)
		for fun_name in k:
			if not func.__name__ in task_gen.prec[fun_name]:
				task_gen.prec[fun_name].append(func.__name__)
		fix_fun_doc(func)
		append_doc(func, 'before', k)
		return func
	return deco
before.__doc__ = TaskGen.before.__doc__
TaskGen.before = before

def after(*k):
	def deco(func):
		exclude_taskgen.append(func.__name__)
		setattr(task_gen, func.__name__, func)
		for fun_name in k:
			if not fun_name in task_gen.prec[func.__name__]:
				task_gen.prec[func.__name__].append(fun_name)
		fix_fun_doc(func)
		append_doc(func, 'after', k)
		return func
	return deco
after.__doc__ = TaskGen.after.__doc__
TaskGen.after = after

# replay existing methods
TaskGen.taskgen_method(TaskGen.to_nodes)
TaskGen.feature('*')(TaskGen.process_source)
TaskGen.feature('*')(TaskGen.process_rule)
TaskGen.before('process_source')(TaskGen.process_rule)
TaskGen.feature('seq')(TaskGen.sequence_order)
TaskGen.extension('.pc.in')(TaskGen.add_pcfile)
TaskGen.feature('subst')(TaskGen.process_subst)
TaskGen.before('process_source','process_rule')(TaskGen.process_subst)

from waflib.Task import Task

Task.__dict__['post_run'].__doc__ = "Update the cache files (executed by threads). Override in subclasses."


from waflib import Configure, Build, Errors
confmeths = []
def conf(f):
	def fun(*k, **kw):
		mandatory = True
		if 'mandatory' in kw:
			mandatory = kw['mandatory']
			del kw['mandatory']

		try:
			return f(*k, **kw)
		except Errors.ConfigurationError as e:
			if mandatory:
				raise e
	confmeths.append(f.__name__)
	f.__doc__ = "\tConfiguration Method bound to :py:class:`waflib.Configure.ConfigurationContext`\n" + (f.__doc__ or '')
	setattr(Configure.ConfigurationContext, f.__name__, fun)
	setattr(Build.BuildContext, f.__name__, fun)
	return f
conf.__doc__ = Configure.conf.__doc__
Configure.conf = conf

Configure.ConfigurationContext.__doc__ = """
	Configure the project.

	Waf tools may bind new methods to this class::

		from waflib.Configure import conf
		@conf
		def myhelper(self):
			print("myhelper")

		def configure(ctx):
			ctx.myhelper()
"""




# Import all tools and build tool->feature map
tool_to_features = {}
import os
lst = [x.replace('.py', '') for x in os.listdir('../../waflib/Tools/') if x.endswith('.py')]
for x in lst:
	if x == '__init__':
		continue
	tool = __import__('waflib.Tools.%s' % x)

	mod = tool.__dict__['Tools'].__dict__[x]
	dc = mod.__all__ = list(mod.__dict__.keys())

	excl = ['before', 'after', 'feature', 'taskgen_method', 'extension']
	if x != 'ccroot':
		excl += ['link_task', 'stlink_task']
	for k in excl:
		try:
			dc.remove(k)
		except:
			pass

	thetool = getattr(tool.Tools, x)
	funcs = dir(thetool)
	for func_name in funcs:
		thefunc = getattr(TaskGen.task_gen, func_name, None)
		if getattr(thefunc, "__name__", None) is None: continue
		for feat in TaskGen.feats:
			funcs = list(TaskGen.feats[feat])
			if func_name in funcs:
				if x not in tool_to_features:
					tool_to_features[x] = []
				tool_to_features[x].append(feat)

	txt = ""
	txt += "%s\n%s\n\n.. automodule:: waflib.Tools.%s\n\n" % (x, "="*len(x), x)
	if x in tool_to_features:
		txt += "Features defined in this module:"
		for feat in sorted(list(set(tool_to_features[x]))):
			link = "../featuremap.html#feature-%s" % feat
			txt += "\n\n* `%s <%s>`_" % (feat, link)

	try: old = open("tools/%s.rst" % x, "r").read()
	except: old = None
	if old != txt:
		with open("tools/%s.rst" % x, "w") as f:
			f.write(txt)

lst = list(TaskGen.feats.keys())
lst.sort()

accu = []
for z in lst:
	meths = TaskGen.feats[z]
	links = []

	allmeths = set(TaskGen.feats[z])
	for x, lst in TaskGen.task_gen.prec.items():
		if x in meths:
			for y in lst:
				links.append((x, y))
				allmeths.add(y)
		else:
			for y in lst:
				if y in meths:
					links.append((x, y))
					allmeths.add(x)

	color = ',fillcolor="#fffea6",style=filled'
	ms = []
	for x in allmeths:
		try:
			m = TaskGen.task_gen.__dict__[x]
		except KeyError:
			raise ValueError("undefined method %r" % x)

		k = "%s.html#%s.%s" % (m.__module__.split('.')[-1], m.__module__, m.__name__)
		if str(m.__module__).find('.Tools') > 0:
			k = 'tools/' + k
		k = '../' + k

		ms.append('\t\t"%s" [style="setlinewidth(0.5)",URL="%s",target="_top",fontname="Vera Sans, DejaVu Sans, Liberation Sans, Arial, Helvetica, sans",height=0.25,shape="rectangle",fontsize=10%s];' % (x, k, x in TaskGen.feats[z] and color or ''))

	for x, y in links:
		ms.append('\t\t"%s" -> "%s" [arrowsize=0.5,style="setlinewidth(0.5)"];' % (x, y))

	rs = '\tdigraph feature_%s {\n\t\tsize="8.0, 12.0";\n%s\n\t}\n' % (z == '*' and 'all' or z, '\n'.join(ms))
	title = "Feature %s" % (z == '*' and '\\*' or z)
	title += "\n" + len(title) * '='

	accu.append("%s\n\n.. graphviz::\n\n%s\n\n" % (title, rs))

f = open('featuremap.rst', 'w')
f.write(""".. _featuremap:

Feature reference
=================

.. include:: featuremap_example.txt
""")
f.write("\n".join(accu))
f.close()

# now for the configuration methods
confmeths.extend('find_program find_file find_perl_program cmd_to_list add_os_flags check_waf_version'.split())
confmeths.sort()
confmeths_dict = {}
accu = []
lst = [x.replace('.py', '') for x in os.listdir('../../waflib/Tools/') if x.endswith('.py')]
for x in lst:
	if x == '__init__':
		continue
	tool = __import__('waflib.Tools.%s' % x)

	mod = tool.__dict__['Tools'].__dict__[x]
	dc = mod.__all__ = list(mod.__dict__.keys())

	thetool = getattr(tool.Tools, x)
	funcs = dir(thetool)
	for func_name in funcs:
		thefunc = getattr(Configure.ConfigurationContext, func_name, None)
		if getattr(thefunc, "__name__", None) is None: continue
		if thefunc:
			confmeths_dict[func_name] = x

for x in confmeths:
	modname = confmeths_dict.get(x, '')
	if modname:
		d = 'tools/%s.html' % modname
		modname = 'Tools.' + modname
	else:
		modname = 'Configure'
		d = '%s.html' % modname

	accu.append('.. _%s: %s#waflib.%s.%s\n' % (x, d, modname, x))
	accu.append('* %s_\n' % x)

f = open('confmap.rst', 'w')
f.write(""".. _confmap:

Configuration methods
=====================

.. include:: confmap_example.txt

""")
f.write("\n".join(accu))
f.close()


#print("Path: %s" % sys.path)

# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.todo', 'sphinx.ext.imgmath', 'sphinx.ext.inheritance_diagram', 'sphinx.ext.graphviz', 'sphinx.ext.viewcode']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Waf'
copyright = u'2005-2016, Thomas Nagy'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
#version = '1.8.10'
# The full version, including alpha/beta/rc tags.
#release = version
#
with open('../../waflib/Context.py', 'r') as f:
	txt = f.read()
	m = re.compile('WAFVERSION=[\'"]([^\'"]+)', re.M).search(txt)
	version = release = m.group(1)

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
try:
	from sphinx import version_info
except ImportError:
	version_info = None
if version_info and (1, 3) <= version_info:
	html_theme = 'classic'
else:
	html_theme = 'default'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> API documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = '_images/waf-64x64.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
html_additional_pages = {'index':'indexcontent.html'}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'wafdoc'


# -- Options for LaTeX output --------------------------------------------------

# The paper size ('letter' or 'a4').
latex_paper_size = 'a4'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'waf.tex', u'waf Documentation',
   u'Thomas Nagy', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'waf', u'waf Documentation',
     [u'Thomas Nagy'], 1)
]

#autodoc_default_flags = ['members', 'no-undoc-members', 'show-inheritance']
autodoc_default_flags = ['members', 'show-inheritance']
autodoc_member_order = 'bysource'

def maybe_skip_member(app, what, name, obj, skip, options):

	# from http://sphinx.pocoo.org/ext/autodoc.html#event-autodoc-skip-member
	# param name: the fully qualified name of the object <- it is not, the name does not contain the module path
	if name in ('__doc__', '__module__', 'Nod3', '__weakref__'):
		return True
	global exclude_taskgen
	if what == 'class' and name in exclude_taskgen:
		return True
	if obj.__doc__:
		return False

def setup(app):
	app.connect('autodoc-skip-member', maybe_skip_member)

