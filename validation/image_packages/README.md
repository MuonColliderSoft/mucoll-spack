# Image package check

CI records the names of every Ubuntu and Spack package installed in each image
and compares them with the matching file in [`baselines/`](baselines). An added
or removed package fails the image build and CI uploads the observed inventory.

Versions are intentionally excluded: Ubuntu security updates and rebuilt Spack
dependencies should not require routine baseline updates. The check is for
changes to the set of packages included in an image. The observed inventory
also records each Spack package's full DAG hash for reference, but hash changes
do not affect the check.

The concretization workflow checks the planned Spack packages against the same
baselines before installation. This catches Spack omissions sooner; the image
check remains authoritative because it also covers Ubuntu packages and the
actual post-install contents.

To run the check against an image:

```bash
docker run --name image-packages \
  -v "$PWD/validation:/validation:ro" \
  --entrypoint python3 <image> \
  /validation/image_packages/check.py --image-type sim --arch amd64 \
  --observed-out /tmp/observed.json
```

If the change is intentional, copy out the new inventory, review it, and
replace the corresponding baseline:

```bash
docker cp image-packages:/tmp/observed.json \
  validation/image_packages/baselines/sim-amd64.json
```
