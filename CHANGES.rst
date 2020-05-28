Changelog
=========

0.10 (2020-05-28)
-----------------

- Moved all the GS types profile logic to `Products.PloneMeeting`,
  by default it will behave like if `imio.zamqp.pm` was enabled.
  [gbastien]

0.9 (2020-04-29)
----------------

- Added test for `MeetingStoreItemsPodTemplateAsAnnexBatchActionForm` to ensure
  that `Temporary QR code` label is not used in stored annex.
  [gbastien]
- Add a `portal_message` when an annex is removed during duplication
  because it holds a `scan_id`.
  [gbastien]

0.8 (2020-03-12)
----------------

- When cloning an item, make sure annexes having a `scan_id` are not kept.
  [gbastien]
- Added test for `get_scan_id` that appends a value `Temporary` if generated
  when pod template still not stored as annex.
  [gbastien]
- Fixed tests after changes in `collective.iconifiedcategory`, do not create an
  annex at the portal root, it is an impossible usecase but create annex in an
  item stored in a PloneMeeting folder.
  [gbastien]

0.7 (2019-05-16)
----------------

- Makes IZPMAnnexPrettyLinkAdapter inherits from PMAnnexPrettyLinkAdapter as it
  is now overrided in Products.PloneMeeting.
  [gbastien]
- Rely on parameter `ToolPloneMeeting.enabledScanDocs` to know if action
  `insert-barcode` is available and to add additional context to the document
  generation helper view.
  [gbastien]
- Make `scan_id` computation work when template is used in a loop template.
  [gbastien]

0.6 (2018-12-04)
----------------

- Fixed tests by using PMLayer as base testing layer and defining correct
  OO_PORT and PYTHON_UNO env variables.
  [gbastien]

0.5 (2018-01-31)
----------------

- Added possibility to save a version of the annex when inserting the barcode
  if parameter `version_when_barcode_inserted` is set to `True` and when the
  scanned file is reinjected if parameter `version_when_scanned_file_reinjected`
  is set to `True` likewise.
  [gbastien]
- Define relevant behaviors for portal_type `annexDecision` using `purge=True`.
  [gbastien]
- Fixed code as `imio.zamqp.core.consumer.file_portal_type` was renamed to
  `imio.zamqp.core.consumer.file_portal_types`, it returns a list of
  portal_types to query to get the existing file, the first of these
  portal_types is used by `imio.zamqp.core.consumer.creation_file_portal_type`
  to determinate portal_type to create.
  [gbastien]
- When updating file, update scan attributes as well : `scan_date`, `scan_user`,
  `page_numbers`, `scanner`, ...
  [gbastien]

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
