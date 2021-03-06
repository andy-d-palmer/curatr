from django.core.exceptions import ValidationError

__author__ = 'palmer'
from django import forms
from standards_review.models import Standard, Adduct, FragmentationSpectrum, Molecule, MoleculeTag, LcInfo, MsInfo
import logging
from django.utils.safestring import mark_safe


def mzml_filename_validator(fn):
    if len(fn.name) < 6 or fn.name[-5:].lower() != ".mzml":
        raise ValidationError("Not a valid mzML file name: " + fn.name)


class MoleculeForm(forms.ModelForm):
    class Meta:
        model = Molecule
        fields = ('name', 'sum_formula', 'lipidmaps_id', 'pubchem_id', 'cas_id', 'chebi_id', 'hmdb_id', 'inchi_code',
                  'solubility', 'tags', 'natural_product')
        widgets = {'tags': forms.widgets.CheckboxSelectMultiple}


class StandardForm(forms.ModelForm):
    class Meta:
        model = Standard
        fields = ('inventory_id','molecule','vendor','vendor_cat','lot_num' ,'location' ,'purchase_date')
        help_texts = {
            'molecule': mark_safe('Molecule not in the list? <a href="/molecule/add/"> add it </a>')
            }


class StandardAddForm(forms.ModelForm):
    class Meta:
        model = Standard
        fields = ('molecule', 'vendor', 'vendor_cat', 'lot_num', 'location', 'purchase_date')
        help_texts = {'molecule': mark_safe('Molecule not in the list? <a href="/molecule/add/"> add it </a>')}


class AdductForm(forms.ModelForm):
    class Meta:
        model = Adduct
        fields = ('nM', 'delta_formula', 'charge')


class StandardBatchForm(forms.Form):
    tab_delimited_file = forms.FileField()


class UploadFileForm(forms.Form):
    mzml_file = forms.FileField(validators=[mzml_filename_validator])
    adducts = forms.ModelMultipleChoiceField(queryset=Adduct.objects.all())
    standards = forms.ModelMultipleChoiceField(queryset=Standard.objects.all().order_by('inventory_id'))
    mass_accuracy_ppm = forms.FloatField(min_value=0.000001, label="MS1 mass accuracy (ppm)")
    quad_window_mz = forms.FloatField(min_value=0.000001, label='Precursor Window (m/z)')
    lc_info = forms.CharField(label="LC Info")
    ms_info = forms.CharField(label="MS Info")
    instrument_info = forms.CharField(label="Instrument Info (obsolete)")
    ionization_method = forms.CharField(label="Ionization Method")
    ion_analyzer = forms.CharField(label="Ion Analyzer")


class FragSpecReview(forms.Form):
    def __init__(self,*args,**kwargs):
        fragSpecId = kwargs.pop('extra')
        self.user = kwargs.pop('user', None)

        super(FragSpecReview, self).__init__(*args, **kwargs)
        for i in fragSpecId:

            logging.debug(i)
            fs = FragmentationSpectrum.objects.get(pk=i)
            logging.debug(fs.dataset)
            initial = 2
            if fs.reviewed:
                if fs.standard:
                    initial = 1
                else:
                    initial = 0
            self.fields['yesno_%s' % i] = forms.ChoiceField(choices=((1, 'Accept'), (0, 'Reject'), (2, 'Unrated')), widget=forms.RadioSelect, label=i, initial=initial)

    def get_response(self):
        for name, value in self.cleaned_data.items():
            if name.startswith('yesno_'):
                yield (self.fields[name].label, value)


class ExportLibrary(forms.Form):
    data_format = forms.ChoiceField(choices=((0, 'mgf'), (1, 'msp'), (2, 'csv'), (3,'EBI json'), (4,'MassBank')),widget=forms.Select)
    class_to_export = forms.ChoiceField(choices=((0, 'all'), (1, 'positive mode'), (2, 'negative mode')), widget=forms.Select)
    #spectra_to_export = forms.ChoiceField(choices=((0, 'Rated Correct'), (1, 'All Rated'), (2, 'ALL MSMS'),), widget=forms.Select)


class MoleculeTagForm(forms.Form):
    class Meta:
        model = MoleculeTag
        fields = ('name',)
