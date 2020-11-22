import enum
from typing import Dict, List

from mongoengine import Document, FloatField, IntField, StringField, ReferenceField, ListField


class TaxType(enum.Enum):
    C_GST = "C_GST"
    S_GST = "S_GST"
    VAT = "VAT"


class Tax(Document):
    value = FloatField(required=True)
    type = StringField(required=True, primary_key=True)

    def as_dict(self) -> Dict:
        return dict(
            id=str(self.pk),
            value=self.value,
            type=self.type
        )


class TaxMapping(Document):
    category = StringField(required=True, primary_key=True)
    taxes = ListField(field=ReferenceField(document_type=Tax), required=True)

    def as_dict(self):
        return dict(
            category=self.category,
            taxes=[
                tax_item.as_dict()
                for tax_item in self.taxes
            ]
        )


def create_tax(**kwargs) -> Tax:
    tax = Tax(
        value=kwargs['value'],
        type=TaxType[kwargs['type']].name
    )
    tax.save()
    return tax


def get_tax_by_id(tax_id: str) -> Tax:
    return Tax.objects(type=tax_id).first()


def get_all() -> List[Tax]:
    return Tax.objects()[:]


def delete_all() -> None:
    Tax.objects().delete()


def create_tax_mapping(category: str, tax_types: List[str]) -> TaxMapping:
    mapping = TaxMapping(category=category, taxes=tax_types)
    mapping.save()
    return mapping


def get_all_tax_mappings() -> List[TaxMapping]:
    return TaxMapping.objects[:]


def get_tax_mapping_by_category(cat: str) -> TaxMapping:
    return TaxMapping.objects(category=cat).first()


def delete_all_tax_mappings() -> None:
    TaxMapping.objects.delete()
