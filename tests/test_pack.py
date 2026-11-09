import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import skill_pack as pack


class PackTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)

    def test_verify(self):
        self.assertTrue(pack.verify()['verified'])

    def test_original_skill_frontmatter(self):
        for skill in pack.SKILLS:
            d=pack.show(skill)
            self.assertIn('name: '+skill,d['markdown'])
            self.assertEqual(d['sha256'],hashlib.sha256(d['markdown'].encode()).hexdigest())

    def test_install_and_readback(self):
        d=pack.install(self.base/'project',pack.SKILLS)
        self.assertEqual(len(d['installed']),3)
        for entry in d['installed']:
            self.assertEqual(Path(entry['path']).read_bytes(),(pack.ROOT/'skills'/entry['skill']/'SKILL.md').read_bytes())
        self.assertFalse(d['executed_skill_instructions'])

    def test_no_overwrite(self):
        pack.install(self.base/'p',pack.SKILLS)
        with self.assertRaises(ValueError):pack.install(self.base/'p',pack.SKILLS)

    def test_single_skill(self):
        self.assertEqual(len(pack.install(self.base/'p',[pack.SKILLS[0]])['installed']),1)

    def test_duplicate_rejected_before_write(self):
        with self.assertRaises(ValueError):pack.install(self.base/'p',[pack.SKILLS[0]]*2)
        self.assertFalse((self.base/'p').exists())

    def test_unknown_rejected_before_write(self):
        with self.assertRaises(ValueError):pack.install(self.base/'p',['../../escape'])
        self.assertFalse((self.base/'p').exists())

    def test_workspace_symlink(self):
        (self.base/'target').mkdir();(self.base/'link').symlink_to(self.base/'target')
        with self.assertRaises(ValueError):pack.install(self.base/'link',pack.SKILLS)

    def test_nested_symlink(self):
        p=self.base/'project';p.mkdir();(self.base/'outside').mkdir();(p/'.agents').symlink_to(self.base/'outside')
        with self.assertRaises(ValueError):pack.install(p,pack.SKILLS)
        self.assertEqual(list((self.base/'outside').iterdir()),[])

    def test_target_symlink(self):
        p=self.base/'project';d=p/'.agents'/'skills'/pack.SKILLS[0];d.mkdir(parents=True)
        (d/'SKILL.md').symlink_to(self.base/'missing')
        with self.assertRaises(ValueError):pack.install(p,pack.SKILLS)
        self.assertFalse((self.base/'missing').exists())

    def test_brief_checks_actual_quote(self):
        d=pack.example('source-grounded-brief')
        self.assertIn(d['result']['answer'],pack.show('source-grounded-brief')['markdown'])
        self.assertFalse(d['result']['publication_approved'])

    def test_draft_never_sends(self):
        d=pack.example('permission-first-followup')
        self.assertTrue(d['result']['draft_eligible_in_example'])
        self.assertFalse(d['result']['send_allowed'])

    def test_measurement_is_deduplicated_and_synthetic(self):
        d=pack.example('measurement-honesty')
        self.assertEqual(d['result']['duplicates_removed'],1)
        self.assertEqual(d['result']['conversion_rate'],.5)
        self.assertFalse(d['result']['production_measurement'])
        self.assertEqual(d['data_class'],'synthetic_public_example')

    def clone(self):
        dest=self.base/'copy';shutil.copytree(pack.ROOT,dest,ignore=shutil.ignore_patterns('.git','__pycache__','demo-workspace','.agents'))
        return dest

    def test_tamper_detected(self):
        dest=self.clone();(dest/'skills'/pack.SKILLS[0]/'SKILL.md').write_text('tampered')
        with patch.object(pack,'ROOT',dest):
            with self.assertRaisesRegex(ValueError,'hash mismatch'):pack.verify()

    def test_extra_private_file_rejected(self):
        dest=self.clone();(dest/'private-notes.txt').write_text('SYNTHETIC NEGATIVE CANARY; no real private data')
        with patch.object(pack,'ROOT',dest):
            with self.assertRaisesRegex(ValueError,'extra or missing'):pack.verify()

    def test_escape_read_rejected(self):
        with self.assertRaises(ValueError):pack.read_public('../outside.txt')

    def test_static_page_has_no_tracking(self):
        page=pack.read_public('web/index.html').decode().lower()
        self.assertNotIn('<script',page);self.assertNotIn('<form',page)
        self.assertNotIn('https://',page);self.assertNotIn('http://',page)

if __name__=='__main__':unittest.main()
