from mako.template import Template
import pyecore.ecore as Ecore
from pyecore.resources.resource import HttpURI
from pyecore.resources import ResourceSet


def ecore_translate(t):
    translate_map = {
        'EString': 'String',
        'EBoolean': 'Boolean',
        'EInt': 'Number',
        'EJavaObject': 'Object',
    }
    return translate_map.get(t.name, t.name)


def uncapitalize(s):
    if not s:
        return s
    return s[0].lower() + s[1:]


class MetamodelStatus(object):
    def __init__(self, has_properties=False, has_traits=False, has_classes=False, has_references=False):
        self.has_properties = has_properties
        self.has_traits = has_traits
        self.has_classes = has_classes
        self.has_references = has_references


class FameGenerator(object):
    template = 'famegen.mako'

    def __init__(self, ePackage):
        self.ePackage = ePackage
        self.entities = []
        self.representation = {}

    @classmethod
    def from_uri(cls, uri, output=None):
        rset = ResourceSet()
        rset.metamodel_registry[Ecore.nsURI] = Ecore
        if uri.startswith("http://") or uri.startswith("http://"):
            uri = HttpURI(uri)
        root = rset.get_resource(uri).contents[0]
        cls.from_epackage(root).generate(output=output,
                                         )
    @classmethod
    def from_epackage(cls, epackage):
        self = cls(epackage)
        self.entities.extend(ec for ec in epackage.eClassifiers if isinstance(ec, Ecore.EClass))
        self.entities.sort(key=lambda ec: len(ec.eAllSuperTypes()))
        return self

    @property
    def classes(self):
        return (e for e in self.entities if not e.interface)

    @property
    def traits(self):
        return (e for e in self.entities if e.interface)

    def generate(self, output=None):
        status = self.validate(self.ePackage)
        mytemplate = Template(filename=self.template)
        rendered = mytemplate.render(generator=self,
                                     translate=ecore_translate,
                                     status=status,
                                     uncapitalize=uncapitalize)
        if output is None:
            print(rendered)
            return
        with open(output, "w") as f:
            f.write(rendered)

    @classmethod
    def validate(cls, ePackage):
        has_classes, has_traits = False, False
        has_references, has_properties = False, False
        assert ePackage.name, 'Package name should be set'
        if ' ' in ePackage.name:
            print(f"WARNING: name of {ePackage.eClass.name} '{ePackage.name}' contains spaces, I remove them")
            ePackage.name = ePackage.name.strip(' ')
        assert ePackage.nsURI, 'Package uri should be set'
        assert ePackage.nsPrefix, 'Package prefix should be set'
        if ' ' in ePackage.nsPrefix:
            print(f"WARNING: name of {ePackage.eClass.name} '{ePackage.nsPrefix}' contains spaces, I remove them")
            ePackage.nsPrefix = ePackage.nsPrefix.strip(' ')
        for x in ePackage.eAllContents():
            if not isinstance(x, (Ecore.EClass, Ecore.EStructuralFeature)):
                continue
            assert x.name, f"Object {x} should have a name"
            if ' ' in x.name:
                print(f"WARNING: name of {x.eClass.name} '{x.name}' contains spaces, I remove them")
                x.name = x.name.strip(' ')
            if isinstance(x, Ecore.EStructuralFeature):
                if not x.eType:
                    print(f"WARNING: attribute/reference {x}, contained by '{x.eContainer().name}' should have a type, I ignore it")
                    x.eContainer().eStructuralFeatures.remove(x)
            has_properties |= isinstance(x, Ecore.EAttribute)
            has_references |= isinstance(x, Ecore.EReference)
            has_traits |= isinstance(x, Ecore.EClass) and x.interface
            has_classes |= isinstance(x, Ecore.EClass) and not x.interface
        return MetamodelStatus(has_properties, has_traits, has_classes, has_references)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("xmi", help="Path or URL of a XMI .ecore metamodel", type=str)
    parser.add_argument("-o", help="Output tonel file. If none is given, stdout is used as output", type=str)
    args = parser.parse_args()
    FameGenerator.from_uri(args.xmi, output=args.o)
