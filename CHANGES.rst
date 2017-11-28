Changelog
=========

0.2 (unreleased)
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
