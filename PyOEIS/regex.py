import re

# OEIS Internal Format parsing
id = re.compile(ur'^%I (A\d+) ?([MN]\d+)? ?([MN]\d+)?', re.M)
unsigned = re.compile(ur'^%[STU] A\d+ ((?:\d+,?)*)', re.M)
signed = re.compile(ur'^%[VWX] A\d+ ((?:-?\d+,?)*)', re.M)
name = re.compile(ur'^%N A\d+ ([^.:]+)([^.]*)', re.M)
reference = re.compile(ur'^%D A\d+ (.+).?', re.M)
link = re.compile(ur'^%H A\d+ (.*)<a href="(.*)">(.*)</a>(.*)', re.M)
formula = re.compile(ur'^%F A\d+ (.+)', re.M)
cross_reference = re.compile(ur'^%Y A\d+ (.+)\.?', re.M)
author = re.compile(ur'^%A A\d+ (.+)', re.M)
offset = re.compile(ur'^%O A\d+ (-?\d+), ?(-?\d+)', re.M)
maple = re.compile(ur'^%p A\d+ (.+)', re.M)
mathematica = re.compile(ur'^%t A\d+ (.+)', re.M)
other_programs = re.compile(ur'^%o A\d+ (.+)', re.M)
error = re.compile(ur'^%E A\d+ (.+)\.?', re.M)
example = re.compile(ur'^%e A\d+ (.+)', re.M)
keywords = re.compile(ur'%K A\d+ [a-zA-Z]+,?', re.M)
comment = re.compile(ur'%C A\d+ (.+)', re.M)
blank_line = re.compile(ur'^\n\s*', re.M)
showing_line = re.compile(ur'Showing \d+-\d+ of (\d+)')

# Maths expression parsing
valid = re.compile(ur'^[()^+-/*!n\d]+$')
parens = re.compile(ur'\([+-/n\d*!^]+\)')
operands = re.compile(ur'(\d+|n)')
fac = re.compile(ur'(\(?[+\d*-/n^]+\)?)!')
opp_paren = re.compile(ur'\)\(')
paren_fac = re.compile(ur'\)fac')
expo = re.compile(ur'\^')
