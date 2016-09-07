def trace(*text, **kwargs):
	global trace_level, trace_outfile;

	level = 3;
	newline = True;

	for k,v in kwargs.items():
		if k == "level":
			level = v;
		elif k == "newline":
			newline = v;

	if level > trace_level: return;

	msg = "";
	for i,t in enumerate(text):
		if i > 0: msg += " "
		msg += str(t);

	if newline:
		print msg;
		msg += '\n';
	else:
		print msg,
		msg += ' ';

	if trace_outfile is not None:
		trace_outfile.write(msg);


def trace_init(level, outfile):
	global trace_level, trace_outfile;

	trace_level = 3 + level;
	trace_outfile = outfile;


def trace_level():
	global trace_level;

	return trace_level;
