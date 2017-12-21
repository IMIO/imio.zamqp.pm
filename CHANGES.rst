Changelog
=========

0.5 (unreleased)
----------------

- Nothing changed yet.


0.4 (2017-12-21)
----------------

- Use the `consume` method from `imio.zamqp.core` to consume the message to
  avoid duplicating code.
  [gbastien]
- Import `PdfReadError` from `PyPDF2`, `imio.helpers` uses it instead
  deprecated `pyPdf`.
  [gbastien]

0.3 (2017-12-06)
----------------

- In field `after_scan_change_annex_type_to`, added possibility to select an
  item_decision_annex on an item_annex and the other way round. This way the
  annex can be turned from an item annex to an item decision annex
  after scan process.
  [gbastien]
- Changed default values for `X` and `Y` coordinates used by the
  `@@insert-barcode` view so it is inserted in the top right corner by default.
  [gbastien]

0.2 (2017-11-28)
----------------

- Added `scan_id` to `AMQPPMDocumentGenerationView.get_base_generation_context`.
  [gbastien]

0.1 (2017-11-27)
----------------

- Initial release.
  [gbastien]
- Added `@@insert-barcode` view.
  [gbastien]
- Make tests rely on PloneMeetingTestCase.
  [gbastien]
- Added possibility to change the `content_category` of an annex when it's
  file is updated and make it configurable on the `ContentCategory` object thru
  the `after_scan_change_annex_type_to` field.
  [gbastien]
- Use helper `imio.zamqp.pm.utils.next_scan_id_pm` that calls
 `imio.zamqp.core.utils.next_scan_id` to be sure that relevant parameters are
  always passed correctly.
  [gbastien]
