# create-github-release GitHub Action

This Action publishes a GitHub Release on a given Tag name with the name of the tag. In addition, it will close the milestone (if available) with the given tag name and creates a new milestone with an increased bugfix version of the previous version.

## Usage
```
github-release:
    needs: release
    runs-on: ubuntu-latest
    if: ${{ needs.release.outputs.released_tag != '' }}
    steps:
      - uses: devonfw-actions/create-github-release@v1
        with:
          release_tag: ${{ needs.release.outputs.released_tag }}
          GHA_TOKEN: ${{ secrets.GHA_TOKEN }}
```
