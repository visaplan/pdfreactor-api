Changelog
=========


1.8.2 (2023-01-20)
------------------

Bugfixes:

- In case of ServerExceptions,
  the `.result` attribute doesn't contain JSON but XML text;
  adjusted `.pdfreactor_says` to handle this
  (and don't raise ValueErrors anymore).

  [tobiasherp]


1.8.1[.post0] (2022-08-24)
--------------------------

Bugfixes:

- Fixed `issue 1`_, "convertAsBinary fails if apiKey is configured"
  [tobiasherp]


1.8.0 (2022-07-12)
------------------

- Initial release, providing a PDFreactor API v8.
  [tobiasherp]

.. _`issue 1`: https://github.com/visaplan/pdfreactor-api/issues/1
