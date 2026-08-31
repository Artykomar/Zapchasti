import re
import uuid

from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from apps.catalog.models import Part, Supplier
from .models import PurchaseLine, PurchaseOrder, Shipment, StockItem


class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ["name", "primary_article", "primary_oem", "brand", "category", "manufacturer", "model_name", "condition", "description", "is_active"]
        labels = {"name": "Название детали", "primary_article": "Артикул", "primary_oem": "OEM-номер", "brand": "Марка автомобиля", "category": "Категория", "manufacturer": "Производитель", "model_name": "Модель", "condition": "Состояние", "description": "Описание", "is_active": "Показывать в каталоге"}
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class StockSettingsForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = ["location", "minimum", "unit_weight_g"]


class OfferForm(forms.Form):
    supplier = forms.ModelChoiceField(label="Поставщик предложения", queryset=Supplier.objects.all(), required=False)
    price_rub = forms.IntegerField(label="Цена продажи, ₽", min_value=0, required=False)
    availability = forms.ChoiceField(label="Наличие у поставщика", choices=Part.Availability.choices)
    delivery = forms.CharField(label="Срок / условия поставщика", max_length=160, required=False)

    def clean(self):
        data = super().clean()
        if (data.get("supplier") is None) != (data.get("price_rub") is None):
            raise ValidationError("Для изменения цены укажите и поставщика, и цену продажи.")
        return data


class AdjustmentForm(forms.Form):
    quantity = forms.IntegerField(label="Изменение количества, шт.", min_value=-1000000, max_value=1000000,
                                  help_text="Например: 5 — приход, −2 — списание. Это изменение, не итоговый остаток.")
    note = forms.CharField(label="Причина", max_length=500, widget=forms.Textarea(attrs={"rows": 2}))
    key = forms.UUIDField(widget=forms.HiddenInput, initial=uuid.uuid4)

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity == 0:
            raise ValidationError("Изменение не может быть нулевым.")
        return quantity


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ["supplier", "reference", "expected_at", "note"]
        labels = {"supplier": "Поставщик"}
        widgets = {"expected_at": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"), "note": forms.Textarea(attrs={"rows": 2})}


class PurchaseLineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["aria-label"] = field.label or name

    class Meta:
        model = PurchaseLine
        fields = ["part", "quantity", "unit_cost_rub"]
        labels = {"part": "Деталь", "quantity": "Количество"}

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if not 1 <= quantity <= 1000000:
            raise ValidationError("Количество должно быть от 1 до 1 000 000.")
        return quantity


PurchaseLineFormSet = inlineformset_factory(PurchaseOrder, PurchaseLine, form=PurchaseLineForm, extra=4,
                                          min_num=1, validate_min=True, max_num=50, validate_max=True, can_delete=True)


class ReceiptForm(forms.Form):
    line_id = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    quantity = forms.IntegerField(label="Принять, шт.", min_value=1, max_value=1000000)
    key = forms.UUIDField(widget=forms.HiddenInput, initial=uuid.uuid4)


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ["recipient_name", "recipient_phone", "city_label", "city_code", "tariff_code", "delivery_point", "address", "weight_g", "length_cm", "width_cm", "height_cm"]
        help_texts = {"city_code": "Числовой код из справочника городов СДЭК, не почтовый индекс.",
                      "tariff_code": "136 — склад → ПВЗ, 137 — склад → дверь. Другие тарифы в этой версии не поддерживаются.",
                      "delivery_point": "Для тарифа 136. Код из справочника СДЭК, например MSK…",
                      "weight_g": "Реальный вес с упаковкой. Вес каждой детали задаётся в её карточке."}

    def clean_recipient_phone(self):
        phone = re.sub(r"[\s()\-]", "", self.cleaned_data["recipient_phone"])
        if not re.fullmatch(r"\+?[0-9]{10,15}", phone):
            raise ValidationError("Укажите телефон с кодом страны, например +7…")
        return phone

    def clean(self):
        data = super().clean()
        tariff = data.get("tariff_code")
        if tariff not in {136, 137}:
            self.add_error("tariff_code", "Поддерживаются тарифы 136 (ПВЗ) и 137 (до двери).")
        if tariff == 136 and (not data.get("delivery_point") or data.get("address")):
            self.add_error("delivery_point", "Для ПВЗ укажите его код и оставьте адрес пустым.")
        if tariff == 137 and (not data.get("address") or data.get("delivery_point")):
            self.add_error("address", "Для доставки до двери укажите адрес и оставьте код ПВЗ пустым.")
        if data.get("delivery_point") and not re.fullmatch(r"[A-Za-z0-9_-]{2,30}", data["delivery_point"]):
            self.add_error("delivery_point", "Неверный формат кода ПВЗ.")
        for name in ["city_code", "weight_g", "length_cm", "width_cm", "height_cm"]:
            if data.get(name) is not None and data[name] <= 0:
                self.add_error(name, "Значение должно быть больше нуля.")
        return data


class ConfirmShipmentForm(forms.Form):
    confirm = forms.BooleanField(label="Подтверждаю данные и отправку заказа в СДЭК. Услуги перевозчика могут быть платными.")
