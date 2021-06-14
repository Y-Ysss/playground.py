from enum import unique, Enum
from typing import Optional, Sequence, Union
from cattr import structure, unstructure
import attr


@unique
class CatBreed(Enum):
    SIAMESE = "siamese"
    MAINE_COON = "maine_coon"
    SACRED_BIRMAN = "birman"


@attr.define
class Cat:
    breed: CatBreed
    names: Sequence[str]


@attr.define
class DogMicrochip:
    chip_id = attr.ib()
    time_chipped: float = attr.ib()


@attr.define
class Dog:
    cuteness: int
    chip: Optional[DogMicrochip]


p = unstructure([Dog(cuteness=1, chip=DogMicrochip(chip_id=1, time_chipped=10.0)),
                 Cat(breed=CatBreed.MAINE_COON, names=('Fluffly', 'Fluffer'))])

print(p)
print(structure(p, list[Union[Dog, Cat]]))
