
#### Dependencies

Install cmake if you do not already have it. If there is not already a folder
called `gtest` in this directory, but just a file with this name, you will need
to populate it:

```
cd <from within top-level `choice` directory>
```
...or, if you already have have the `choice` ROS package installed from source,
you could just:

```
roscd choice
```
...then:

```
git submodule update --init --recursive
```
This will download the `gtest` source code, which I use for the library unit
tests.

TODO latest? how to get it to just download the same version I'm using? is that
actually what's happening?

#### Running the tests

Starting in this directory, run the following:
```
mkdir build
cd build
cmake ..
make
./multishock_tests
```

#### TODO 
- edit `CMakeLists.txt` to take advantage of ExternalProject git submodule 
  features, and include instructions here if necessary
- setup "continuous integration" testing with Travis CI
