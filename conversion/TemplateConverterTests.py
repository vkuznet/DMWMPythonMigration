import unittest

from TemplateConverter import TemplateConverter


class TestConverter(unittest.TestCase):
    def test_multiplePlaceHolders(self):
        lines = ["$from_res&#8212;$to_res records out of $nrows.\n"]
        converter = TemplateConverter(lines, "test_notPlaceholder")
        convertedLines = converter.getFileLines()
        self.assertEqual("{{from_res}}&#8212;{{to_res}} records out of {{nrows}}.\n", convertedLines[0])

    def test_multiplePlaceHolders1(self):
        lines = ["$quote($jsoncode)"]
        converter = TemplateConverter(lines, "test_placeholderFuncion")
        convertedLines = converter.getFileLines()
        self.assertEqual("{{quote(jsoncode)}}", convertedLines[0])

    def test_multiplePlaceHolders2(self):
        lines = ["<td><a href='$base/task?id=$quote_plus($parent)'>$quote($parent)</a></td>"]
        converter = TemplateConverter(lines, "test_notPlaceholder")
        convertedLines = converter.getFileLines()
        self.assertEqual("<td><a href='{{base}}/task?id={{quote_plus(parent)}}'>{{quote(parent)}}</a></td>",
                         convertedLines[0])

    def test_multiplePlaceHolders3(self):
        lines = ["$quote($jsoncode[$li[a(1)]])"]
        converter = TemplateConverter(lines, "test_placeholderFuncion")
        convertedLines = converter.getFileLines()
        self.assertEqual("{{quote(jsoncode[li[a(1)]])}}", convertedLines[0])

    def test_multiplePlaceHolders4(self):
        lines = ["$quote($jsoncode[1]) aa $jsoncode[1]. $jsoncode_a($quote($la))"]
        converter = TemplateConverter(lines, "test_placeholderFuncion")
        convertedLines = converter.getFileLines()
        self.assertEqual("{{quote(jsoncode[1])}} aa {{jsoncode[1]}}. {{jsoncode_a(quote(la))}}", convertedLines[0])

    def test_multiplePlaceHolders5(self):
        lines = ["($from_res) aa"]
        converter = TemplateConverter(lines, "test_notPlaceholder")
        convertedLines = converter.getFileLines()
        self.assertEqual("({{from_res}}) aa", convertedLines[0])

    def test_simplePlaceholders(self):
        lines = ["$from"]
        converter = TemplateConverter(lines, "test_notPlaceholder")
        convertedLines = converter.getFileLines()
        self.assertEqual("{{from}}", convertedLines[0])

    def test_placeholderFuncion(self):
        lines = ["$qoute($stuff.morestuff(anmore()))\n"]
        converter = TemplateConverter(lines, "test_placeholderFuncion")
        convertedLines = converter.getFileLines()
        self.assertEqual("{{qoute(stuff.morestuff(anmore()))}}\n", convertedLines[0])

    def test_placeholderFuncion2(self):
        lines = ["<li>$quote($key): $quote($val)</li>"]
        converter = TemplateConverter(lines, "test_placeholderFuncion")
        convertedLines = converter.getFileLines()
        self.assertEqual("<li>{{quote(key)}}: {{quote(val)}}</li>", convertedLines[0])
    def test_placeholderFuncion2(self):
        lines = ["< a href = \"javascript:Transition(-$width)\" style = \"background-color:#fff\" >"]
        converter = TemplateConverter(lines, "test_placeholderFuncion")
        convertedLines = converter.getFileLines()
        self.assertEqual("< a href = \"javascript:Transition(-{{width}})\" style = \"background-color:#fff\" >",
                         convertedLines[0])

    def test_set(self):
        lines = ["#set timestamp = $time.strftime(\"%a, %d %b %Y %H:%M:%S GMT\", $time.gmtime())"]
        converter = TemplateConverter(lines, "test_set")
        convertedLines = converter.getFileLines()
        self.assertEqual("{%- set timestamp = time.strftime(\"%a, %d %b %Y %H:%M:%S GMT\", time.gmtime()) %}",
                         convertedLines[0])

    def test_placeholderAsHref(self):
        lines = ["<a href=\"$newUrl\">next</a> |"]
        converter = TemplateConverter(lines, "test_placeholderAsHref")
        convertedLines = converter.getFileLines()
        self.assertEqual("<a href=\"{{newUrl}}\">next</a> |", convertedLines[0])

    def test_placeholdersKeywords(self):
        lines = ["$quote($json.dumps($result, indent=4, default=str))"]
        converter = TemplateConverter(lines, "test_placeholderAsHref")
        convertedLines = converter.getFileLines()
        self.assertEqual("{{quote(json.dumps(result, indent=4, default=str))}}", convertedLines[0])

    def test_placeholdersMultiple(self):
        lines = ["<b>$das</b> $quote($row.get(\"description\", \"N/A\"))"]
        converter = TemplateConverter(lines, "test_placeholdersMultiple")
        convertedLines = converter.getFileLines()
        self.assertEqual("<b>{{das}}</b> {{quote(row.get(\"description\", \"N/A\"))}}", convertedLines[0])

    def test_comments(self):
        lines = ["##<div><h3>Result $quote($result.get($task_id))</h3></div>\n"]
        converter = TemplateConverter(lines, "test_comments")
        convertedLines = converter.getFileLines()
        self.assertEqual("{#-<div><h3>Result {{quote(result.get(task_id))}}</h3></div> #}\n", convertedLines[0])

    def test_longComment(self):
        lines = ["#####if $lfn!=$lfnList[-1]\n"]
        converter = TemplateConverter(lines, "test_longComment")
        convertedLines = converter.getFileLines()
        self.assertEqual("{#-if {{lfn}}!={{lfnList[-1]}} #}\n", convertedLines[0])

    def test_specChars(self):
        lines = ["\\$('$highlight').addClassName('box_attention').show()", "\\#slide_cards span {"]
        converter = TemplateConverter(lines, "test_specChars")
        convertedLines = converter.getFileLines()
        self.assertEqual("$('$highlight').addClassName('box_attention').show()", convertedLines[0])
        self.assertEqual("#slide_cards span {", convertedLines[1])

    def test_for(self):
        lines = ["#for row in $daskeys"]
        converter = TemplateConverter(lines, "test_for")
        convertedLines = converter.getFileLines()
        self.assertEqual("{% for row in daskeys -%}", convertedLines[0])

    def test_ifBlock(self):
        lines = [
            "#if $dbs==$dbs_global",
            "#set msg=\"<b>default DBS instance</b>\"",
            "#elif $dbs.startswith('prod')",
            "#set msg=\"<em>production DBS instance</em>\"",
            "#elif $dbs.startswith('int')",
            "#set msg=\"<em>integration DBS instance</em>\"",
            "#elif $dbs.startswith('dev')",
            "#set msg=\"<em>development DBS instance</em>\"",
            "#else",
            "#set msg=\"\"",
            "#end if",
        ]
        linesResult = [
            "{% if dbs==dbs_global -%}",
            "{%- set msg=\"<b>default DBS instance</b>\" %}",
            "{% elif dbs.startswith('prod') %}",
            "{%- set msg=\"<em>production DBS instance</em>\" %}",
            "{% elif dbs.startswith('int') %}",
            "{%- set msg=\"<em>integration DBS instance</em>\" %}",
            "{% elif dbs.startswith('dev') %}",
            "{%- set msg=\"<em>development DBS instance</em>\" %}",
            "{% else -%}",
            "{%- set msg=\"\" %}",
            "{%- endif -%}",
        ]
        converter = TemplateConverter(lines, "test_ifBlock")
        convertedLines = converter.getFileLines()
        self.assertEqual(linesResult, convertedLines)

    def test_silent(self):
        lines = ["#silent $init_dbses.remove($inst)"]
        converter = TemplateConverter(lines, "test_silent")
        convertedLines = converter.getFileLines()
        self.assertEqual("{{- \"\" if  init_dbses.remove(inst)}}", convertedLines[0])

    def test_str(self):
        lines = ["#set newUrl = $url + \"&amp;idx=\" + $str($last) + \"&amp;limit=\" + $str($limit)"]
        converter = TemplateConverter(lines, "test_str")
        convertedLines = converter.getFileLines()
        self.assertEqual("{%- set newUrl = url + \"&amp;idx=\" + last| string + \"&amp;limit=\" + limit| string %}",
                         convertedLines[0])

    def test_lenRange(self):
        lines = ["#for idx in $range(0, len($cards))"]
        converter = TemplateConverter(lines, "test_lenRange")
        convertedLines = converter.getFileLines()
        self.assertEqual("{% for idx in range(0, cards| count) -%}", convertedLines[0])


if __name__ == '__main__':
    unittest.main()
