from __future__ import generator_stop

from click.testing import CliRunner

from ttc_api_scraper import cli


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.output.startswith('Usage:')
    assert 'Show this message and exit.' in result.output
    assert 0 == result.exit_code

    # Make sure commands are listed
    lines = result.output.split('\n')
    for idx, line in enumerate(lines):
        if line == 'Commands:':
            assert '  archive  Download month (YYYYMM) of data from database...' == lines[idx + 1]
            assert '  scrape   Run the scraper' == lines[idx + 2]
            assert '' == lines[idx + 3]
            assert idx + 3 == len(lines) - 1
            break
    else:
        assert False, 'Cannot find commands in output'
