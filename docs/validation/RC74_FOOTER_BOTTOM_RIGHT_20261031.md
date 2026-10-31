# RC74 footer position / Posizione Footer

- Default geometry: x=0, y=94, width=100, height=6 percent of canvas.
- Center text: session name, horizontally centered.
- Page number: absolute `right: 0; bottom: 0` of footer, therefore right/bottom canvas edge at default geometry.
- Participant page stage renders footer as a positioned widget inside 16:9 page, not a duplicate block beneath it.
- PowerPoint right textbox reaches entire page right/bottom, with bottom vertical anchor, right horizontal alignment and no inset.
- Automated regressions: `python3 -m unittest tools.tests.test_rc74_footer_corner tools.tests.test_rc73_slide_master -v`.
- Manual follow-up: verify desktop/mobile browser geometry and editable PPTX output in post-commit CI.
- This cycle earns no additional RC acceptance credit pending CI: 84.75%; no publication.
