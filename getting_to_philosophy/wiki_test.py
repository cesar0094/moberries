import unittest
import wiki

class EndToEndTest(unittest.TestCase):

    TEST_CASES = [
        ['https://en.wikipedia.org/wiki/Mathematics',
         'Mathematics > Quantity > Counting > Element (mathematics) > *Looped to Mathematics*',
         "Should not go into footnotes"],

        ['https://en.wikipedia.org/wiki/United_States',
         "United States > Country > Political geography > Politics > Decision-making > Psychology > Science > Knowledge > Fact > Reality > Object of the mind > Object (philosophy) > Philosophy",
         "Should not go into the coordinates element on the top-right"],

        ['https://en.wikipedia.org/wiki/Switzerland',
         "Switzerland > Sovereign state > International law > Nation > Community > Social norm > Sociology > Society > Social group > Social science > Discipline (academia) > Knowledge > Fact > Reality > Object of the mind > Object (philosophy) > Philosophy",
         "Should travel from Switzerland correctly"],

        ['https://en.wikipedia.org/wiki/Competition',
         "Competition > Rivalry > *Looped to Competition*",
         "Should loop in compretition"],

        ['https://en.wikipedia.org/wiki/Lachheb',
         "Lachheb > Adli Lachheb > Association football > Team sport > Sport > Competition > Rivalry > *Looped to Competition*",
         "Should get the first link from a 'li'"],

        ['https://en.wikipedia.org/wiki/Wikipedia:Red_link',
         "Wikipedia:Red link > Wikipedia:Viewing deleted content > Wikipedia:Administrators > Wikipedia:Blocking policy > *Looped to Wikipedia:Administrators*",
         "Should avoid red links"],

        ['https://en.wikipedia.org/wiki/Physics',
         "Physics > Natural science > Branches of science > Science > Knowledge > Fact > Reality > Object of the mind > Object (philosophy) > Philosophy",
         "Should handle nested parenthesis with and link with two words"],

        ['https://en.wikipedia.org/wiki/Insect',
         "Insect > Hexapoda > Arthropod > Invertebrate > Animal > Multicellular organism > Organism > Biology > Natural science > Branches of science > Science > Knowledge > Fact > Reality > Object of the mind > Object (philosophy) > Philosophy",
         "Should not look into boxes for links"],

        ['https://en.wikipedia.org/wiki/Association_football',
         "Association football > Team sport > Sport > Competition > Rivalry > *Looped to Competition*",
         "Should not take footnotes as links"],

        ['https://en.wikipedia.org/wiki/Planet',
         "Planet > Astronomical object > Physical object > Three-dimensional space > Dimension > Physics > Natural science > Branches of science > Science > Knowledge > Fact > Reality > Object of the mind > Object (philosophy) > Philosophy",
         "Should not go to wiktionary.org"],

        ['https://en.wikipedia.org/wiki/Saxony-Anhalt',
         "Saxony-Anhalt > States of Germany > Germany > Central Europe > Europe > Continent > Landmass > Land > Earth > Planet > Astronomical object > Physical object > Three-dimensional space > Dimension > Physics > Natural science > Branches of science > Science > Knowledge > Fact > Reality > Object of the mind > Object (philosophy) > Philosophy",
         "Should handle word in parethesis when it is also outside of the parenthesis: (German ...) ... Germany."],

        ['https://en.wikipedia.org/wiki/Ethology',
         "Ethology > Scientific method > Empirical evidence > Information > Uncertainty > Epistemology > Philosophy",
         "Should handle different from the usual path"],

        ['https://en.wikipedia.org/wiki/Edith_Oldrup',
         "Edith Oldrup > Soprano > Classical music > Art music > Light music > *Looped to Classical music*",
         "Should loop to classical music"],

        ['https://en.wikipedia.org/wiki/Kannada',
         "Kannada > Dravidian languages > Language family > Language > Linguistic system > Ferdinand de Saussure > Switzerland > Sovereign state > International law > Nation > Community > Social norm > Sociology > Society > Social group > Social science > Discipline (academia) > Knowledge > Fact > Reality > Object of the mind > Object (philosophy) > Philosophy",
         "Should not loop back to same page if title is in parenthesis"],

        ['https://en.wikipedia.org/wiki/American_Board_of_Internal_Medicine',
         "American Board of Internal Medicine > 501(c)(3) organization > Internal Revenue Code > United States Statutes at Large > Act of Congress > Statute > Legislature > Deliberative assembly > Parliamentary procedure > Procedural law > Court > Government > State (polity) > Politics > Decision-making > Psychology > Science > Knowledge > Fact > Reality > Object of the mind > Object (philosophy) > Philosophy",
         "Should follow links which have parentheses."],

        ['https://en.wikipedia.org/wiki/César_Award_for_Best_Film',
         "César Award for Best Film > César Award > Cinema of France > Film industry > Filmmaking > Film > Cinematography > *Looped to Film*",
         "Should look into bold text links"],

        ['https://en.wikipedia.org/wiki/Topless_(film)',
         "Topless (film) > Erika Okuda > *Looped to Topless (film)*",
         "Should look from paragraphs to lists"],

        ['https://en.wikipedia.org/wiki/Herpetological_society',
         "Herpetological society > Portal:Amphibians and reptiles > Portal:Amphibians > *Page without a valid first link found*",
         "Should look into bold text links of lists"],

        ['https://en.wikipedia.org/wiki/Folk_Music',
         "Folk music > Roots revival > Pop music > Popular music > Music industry > Musical composition > Originality > Replica > Copying > Information > Uncertainty > Epistemology > Philosophy",
         "Should look into bold text links of lists"],
    ]

    def test_list(self):
        for test_input, expected, message in self.TEST_CASES:
            path = wiki.get_to_philosophy(test_input)
            self.assertEqual(" > ".join(path), expected, message)


class ExceptionsTest(unittest.TestCase):
    TEST_CASES = [
        ['https://en.wikipedia.org/wiki/Idontexist404', wiki.InvalidResponse, "Should wrap around a non-200"],
    ]

    def test_list(self):
        for test_input, exception, message in self.TEST_CASES:
            with self.assertRaises(exception) as cm:
                path = wiki.get_to_philosophy(test_input)


class RemoveParenthesesTest(unittest.TestCase):
    TEST_CASES = [
        [ "i am outside (inside, inside2) here too" ,
            "i am outside  here too",
            "Should split simple parenthesis"],
        [ "i am outside (inside (this is nested) inside2) here too",
            "i am outside  here too",
            "Should split nested parenthesis"],
        [ "i am outside 3-d (inside the parenthesis) inbetween (inside2 parenthesis2) here too",
            "i am outside 3-d  inbetween  here too",
            "Should leave hyphens"],
        [ "i ám â ünicode ßtring (inside1, some stuff) inbetween (inside2) here too",
            "i ám â ünicode ßtring  inbetween  here too",
            "Should handle unicode"],
        [ "i am a link:with:colons (inside1, some stuff) inbetween (inside2) here too",
            "i am a link:with:colons  inbetween  here too",
            "Should leave colons"],
        [ "this is a (parenthesis (nested) still parenthesis) and then we have (another (nested2)) and a (single)",
            "this is a  and then we have  and a ",
            "Should deal with multiple nested parenthesis"],
        [ "this is a (parenthesis (nested (triple) ) still parenthesis) and then we have (another (nested2)) and a (single)",
            "this is a  and then we have  and a ",
            "Should deal with multiple nested parenthesis"],
        [ "this is a (parenthesis (nested (triple) ) still parenthesis) and ) then we have (another (nested2)) and a (single)",
            "this is a  and  then we have  and a ",
            "Should deal remove unexpected closing parenthesis"],
        [ "this is a (parenthesis (nested (triple) ) still parenthesis) and then we have ( an open",
            "this is a  and then we have  and then we have  an open",
            "Should deal remove unexpected open parenthesis"]
    ]

    def test_list(self):
        for test_input, expected, message in self.TEST_CASES:
            self.assertEqual(wiki.remove_parentheses(test_input), expected, message)

if __name__ == '__main__':
    unittest.main()
