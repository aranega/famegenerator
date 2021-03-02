<%
pname = generator.ePackage.name.capitalize()
classname = pname + 'Generator'
handled = set()
%>
Class {
  #name : #${classname},
  #superclass : #FamixMetamodelGenerator,
  #instVars : [
  % for ec in generator.entities:
    '${uncapitalize(ec.name)}'${'' if loop.last else ','}
  % endfor
  ],
  #category : #${pname}
}


{ #category : #accessing }
${classname} class >> packageName [
	^ '${pname}'
]

{ #category : #accessing }
${classname} class >> prefix [
	^ '${generator.ePackage.nsPrefix.capitalize()}'
]
% if status.has_classes:


{ #category : #definition }
${classname} >> defineClasses [
  super defineClasses.

  % for ec in generator.classes:
  ${uncapitalize(ec.name)} := builder newClassNamed: #${ec.name}.
  % endfor
]
% endif
% if status.has_classes or status.has_traits:

{ #category : #definition }
${classname} >> defineHierarchy [
  super defineHierarchy.

  % for ec in generator.entities:
   % for super in ec.eSuperTypes:
    % if super.eResource is ec.eResource:
  ${uncapitalize(ec.name)} --|> ${uncapitalize(super.name)}.
    % else:
  ${uncapitalize(ec.name)} --|> #${super.name}.
    % endif
   % endfor
  % endfor
]
% endif
% if status.has_properties:

{ #category : #definition }
${classname} >> defineProperties [
  super defineProperties.

  % for ec in generator.entities:
   % for attr in ec.eAttributes:
  ${uncapitalize(ec.name)} property: #${attr.name} type: #${translate(attr.eType)}.
   % endfor
  % endfor
]
% endif
% if status.has_references:

{ #category : #definition }
${classname} >> defineRelations [
  super defineRelations.

 % for ec in generator.entities:
   % for attr in (a for a in ec.eReferences if not a.derived):
     % if attr not in handled:
   (${uncapitalize(ec.name)} property: #${attr.name}) ${linksymbol(attr)} (${uncapitalize(attr.eType.name)} property: #${attr.eOpposite.name if attr.eOpposite else uncapitalize(ec.name)}).
<% handled.add(attr); handled.add(attr.eOpposite) %>\
     % endif
   % endfor
 % endfor
]
% endif
% if status.has_traits:

{ #category : #definition }
${classname} >> defineTraits [
  super defineTraits .

  % for ec in generator.traits:
  ${uncapitalize(ec.name)} := builder newTraitNamed: #${ec.name}.
  % endfor
]
% endif
<%def name="linksymbol(feature)"> \
% if feature in handled:
<% return '' %>\
% endif
% if feature.eOpposite and feature.eOpposite.many:
*-\
% elif feature.containment:
${'<>'}-\
% else:
-\
% endif
% if feature.many:
*\
% elif feature.eOpposite and feature.eOpposite.containment:
${'<>'}\
% endif
</%def>
